"""
Error handling và logging cho Study Buddy
"""
import streamlit as st
import traceback
import logging
from datetime import datetime
from typing import Optional, Any, Callable, Dict
from functools import wraps
from ..config.constants import ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('study_buddy.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StudyBuddyError(Exception):
    """Base exception cho Study Buddy"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class FileProcessingError(StudyBuddyError):
    """Exception cho file processing errors"""
    pass

class DatabaseError(StudyBuddyError):
    """Exception cho database errors"""
    pass

class LLMConnectionError(StudyBuddyError):
    """Exception cho LLM connection errors"""
    pass

class ValidationError(StudyBuddyError):
    """Exception cho validation errors"""
    pass

class AuthenticationError(StudyBuddyError):
    """Exception cho authentication errors"""
    pass

def handle_error(error: Exception, context: str = "", show_user: bool = True) -> Optional[str]:
    """
    Xử lý lỗi một cách nhất quán
    
    Args:
        error: Exception object
        context: Ngữ cảnh khi lỗi xảy ra
        show_user: Có hiển thị lỗi cho user không
        
    Returns:
        Error message string hoặc None
    """
    error_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # Log error với detail
    logger.error(f"[{error_id}] {context}: {str(error)}")
    logger.error(f"[{error_id}] Traceback: {traceback.format_exc()}")
    
    # Xác định loại lỗi và message phù hợp
    if isinstance(error, StudyBuddyError):
        error_message = error.message
        error_code = error.error_code
    elif isinstance(error, FileNotFoundError):
        error_message = "Không tìm thấy file được yêu cầu"
        error_code = "file_not_found"
    elif isinstance(error, PermissionError):
        error_message = "Không có quyền thực hiện thao tác này"
        error_code = "permission_denied"
    elif isinstance(error, ConnectionError):
        error_message = "Lỗi kết nối mạng"
        error_code = "network_error"
    elif isinstance(error, TimeoutError):
        error_message = "Thao tác timeout"
        error_code = "timeout_error"
    elif "supabase" in str(error).lower():
        error_message = ERROR_MESSAGES.get('database_connection_failed', 'Lỗi database')
        error_code = "database_error"
    elif "openai" in str(error).lower() or "llm" in str(error).lower():
        error_message = ERROR_MESSAGES.get('llm_connection_failed', 'Lỗi LLM')
        error_code = "llm_error"
    else:
        error_message = f"Lỗi không xác định: {str(error)}"
        error_code = "unknown_error"
    
    # Hiển thị cho user nếu cần
    if show_user:
        st.error(f"❌ {error_message}")
        
        # Hiển thị error ID cho debugging (nếu ở development mode)
        if st.session_state.get('debug_mode', False):
            st.caption(f"Error ID: {error_id}")
    
    return error_message

def safe_execute_with_retry(func: Callable, max_retries: int = 3, delay: float = 1.0, 
                          context: str = "", show_user: bool = True) -> tuple[bool, Any, Optional[str]]:
    """
    Execute function với enhanced retry mechanism và smart error recovery
    
    Args:
        func: Function to execute
        max_retries: Số lần retry tối đa
        delay: Delay giữa các lần retry (seconds)
        context: Ngữ cảnh thực hiện
        show_user: Có hiển thị lỗi cho user không
        
    Returns:
        Tuple[bool, Any, Optional[str]]: (success, result, error_message)
    """
    import time
    import random
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func()
            
            # Log successful retry if previous attempts failed
            if attempt > 0:
                logger.info(f"{context} - Success on attempt {attempt + 1}")
            
            return True, result, None
            
        except Exception as e:
            last_error = e
            
            # Enhanced error categorization for smart retry
            should_retry = _should_retry_error(e, attempt, max_retries)
            
            if attempt < max_retries and should_retry:
                # Adaptive delay with jitter to prevent thundering herd
                adaptive_delay = delay * (1.5 ** attempt) + random.uniform(0, 0.5)
                
                logger.warning(f"{context} - Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)[:100]}. Retrying in {adaptive_delay:.1f}s...")
                
                # Progressive backoff with circuit breaker pattern
                time.sleep(adaptive_delay)
                
                # Special handling for specific error types
                if "rate limit" in str(e).lower():
                    time.sleep(additional_rate_limit_delay(attempt))
                elif "timeout" in str(e).lower():
                    # Increase timeout tolerance on retry
                    pass
                    
            else:
                error_message = handle_error(e, f"{context} (final attempt)", show_user)
                return False, None, error_message
    
    # This should never be reached, but just in case
    error_message = handle_error(last_error or Exception("Max retries exceeded"), context, show_user)
    return False, None, error_message

def _should_retry_error(error: Exception, attempt: int, max_retries: int) -> bool:
    """Determine if an error should trigger a retry based on error type and context"""
    error_str = str(error).lower()
    
    # Always retry network/connection errors
    if any(keyword in error_str for keyword in ['connection', 'timeout', 'network', 'refused']):
        return True
    
    # Retry rate limit errors with longer delays
    if any(keyword in error_str for keyword in ['rate limit', '429', 'quota', 'capacity']):
        return True
    
    # Retry temporary service errors
    if any(keyword in error_str for keyword in ['503', '502', '504', 'temporary', 'unavailable']):
        return True
    
    # Don't retry authentication/permission errors
    if any(keyword in error_str for keyword in ['401', '403', 'unauthorized', 'forbidden', 'permission']):
        return False
    
    # Don't retry validation errors
    if any(keyword in error_str for keyword in ['400', 'bad request', 'invalid', 'validation']):
        return False
    
    # Retry unknown errors up to first few attempts
    return attempt < min(2, max_retries)

def additional_rate_limit_delay(attempt: int) -> float:
    """Calculate additional delay for rate limit errors"""
    base_delay = 2.0  # Base delay for rate limits
    return base_delay * (2 ** attempt)  # Exponential backoff for rate limits

def error_boundary(context: str = "", show_user: bool = True, fallback_value: Any = None):
    """
    Decorator để wrap functions với error handling
    
    Args:
        context: Ngữ cảnh cho logging
        show_user: Có hiển thị lỗi cho user không
        fallback_value: Giá trị trả về khi có lỗi
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context or func.__name__, show_user)
                return fallback_value
        return wrapper
    return decorator

@error_boundary("File upload validation", show_user=True)
def validate_and_process_file(uploaded_file, processor):
    """Validate và xử lý file upload với error handling"""
    from .validators import FileValidator
    
    # Validate file
    is_valid, error_msg = FileValidator.validate_file(uploaded_file)
    if not is_valid:
        raise ValidationError(error_msg, "file_validation_failed")
    
    # Process file
    content = processor.process_document(uploaded_file)
    if not content:
        raise FileProcessingError("Không thể xử lý nội dung file", "file_processing_failed")
    
    return content

@error_boundary("Database operation", show_user=True)
def safe_database_operation(operation_func, *args, **kwargs):
    """Thực hiện database operation với error handling"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        if "connection" in str(e).lower():
            raise DatabaseError(ERROR_MESSAGES['database_connection_failed'], "db_connection_failed")
        elif "timeout" in str(e).lower():
            raise DatabaseError(ERROR_MESSAGES['timeout_error'], "db_timeout")
        else:
            raise DatabaseError(f"Database error: {str(e)}", "db_operation_failed")

@error_boundary("LLM operation", show_user=True)
def safe_llm_operation(llm_func, *args, **kwargs):
    """Thực hiện LLM operation với error handling"""
    try:
        return llm_func(*args, **kwargs)
    except Exception as e:
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise LLMConnectionError(ERROR_MESSAGES['llm_connection_failed'], "llm_connection_failed")
        else:
            raise LLMConnectionError(f"LLM error: {str(e)}", "llm_operation_failed")

def show_success_message(key: str, **kwargs):
    """Hiển thị success message"""
    message = SUCCESS_MESSAGES.get(key, "Thao tác thành công")
    if kwargs:
        message = message.format(**kwargs)
    st.success(f"✅ {message}")
    logger.info(f"Success: {message}")

def show_warning_message(key: str, **kwargs):
    """Hiển thị warning message"""
    message = WARNING_MESSAGES.get(key, "Cảnh báo")
    if kwargs:
        message = message.format(**kwargs)
    st.warning(f"⚠️ {message}")
    logger.warning(f"Warning: {message}")

def show_error_message(key: str, **kwargs):
    """Hiển thị error message"""
    message = ERROR_MESSAGES.get(key, "Có lỗi xảy ra")
    if kwargs:
        message = message.format(**kwargs)
    st.error(f"❌ {message}")
    logger.error(f"Error: {message}")

def check_authentication(func):
    """Decorator để kiểm tra authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(st.session_state, 'user_id') or not st.session_state.user_id:
            raise AuthenticationError(ERROR_MESSAGES['authentication_required'], "auth_required")
        return func(*args, **kwargs)
    return wrapper

def require_session(func):
    """Decorator để kiểm tra session validity"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get('current_session_id'):
            raise ValidationError(ERROR_MESSAGES['invalid_session'], "invalid_session")
        return func(*args, **kwargs)
    return wrapper

class ProgressTracker:
    """Enhanced class để track progress của long-running operations với smart UI updates"""
    
    def __init__(self, total_steps: int, description: str = "Processing...", show_percentage: bool = True):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.show_percentage = show_percentage
        self.start_time = datetime.now()
        
        # Enhanced UI elements
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.eta_text = st.empty() if show_percentage else None
        
    def update(self, step_description: str = "", increment: int = 1):
        """Enhanced update with ETA calculation"""
        self.current_step += increment
        progress = min(self.current_step / self.total_steps, 1.0)  # Clamp to 1.0
        
        self.progress_bar.progress(progress)
        
        # Calculate ETA
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if self.current_step > 0 and progress < 1.0:
            estimated_total_time = elapsed_time / progress
            eta_seconds = estimated_total_time - elapsed_time
            eta_str = f" (ETA: {int(eta_seconds)}s)" if eta_seconds > 0 else ""
        else:
            eta_str = ""
        
        # Update status text
        if self.show_percentage:
            percentage = int(progress * 100)
            status_msg = f"{self.description} - {step_description} ({percentage}%{eta_str})"
        else:
            status_msg = f"{self.description} - {step_description} ({self.current_step}/{self.total_steps})"
            
        self.status_text.text(status_msg)
        
        # Update ETA text if available
        if self.eta_text and eta_str:
            self.eta_text.caption(f"Elapsed: {int(elapsed_time)}s{eta_str}")
    
    def set_step(self, step_number: int, step_description: str = ""):
        """Set specific step number (useful for non-linear progress)"""
        self.current_step = step_number
        self.update(step_description, increment=0)
    
    def complete(self, final_message: str = "Hoàn thành!", show_stats: bool = True):
        """Complete progress tracking with optional statistics"""
        self.progress_bar.progress(1.0)
        
        if show_stats:
            total_time = (datetime.now() - self.start_time).total_seconds()
            final_msg = f"{final_message} (Hoàn thành trong {total_time:.1f}s)"
        else:
            final_msg = final_message
            
        self.status_text.text(final_msg)
        
        if self.eta_text:
            self.eta_text.empty()
        
    def error(self, error_message: str = "Có lỗi xảy ra"):
        """Handle error state in progress tracker"""
        self.status_text.text(f"❌ {error_message}")
        if self.eta_text:
            self.eta_text.empty()
            
    def cleanup(self, delay: float = 2.0):
        """Clean up progress elements with optional delay"""
        import time
        if delay > 0:
            time.sleep(delay)
        
        try:
            self.progress_bar.empty()
            self.status_text.empty()
            if self.eta_text:
                self.eta_text.empty()
        except:
            pass

class ErrorRecoveryManager:
    """Manager class for handling error recovery strategies"""
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        
    def register_recovery_strategy(self, error_type: type, strategy_func: Callable):
        """Register a recovery strategy for specific error type"""
        self.error_strategies[error_type] = strategy_func
        
    def attempt_recovery(self, error: Exception, context: str) -> bool:
        """Attempt to recover from an error using registered strategies"""
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            try:
                recovery_func = self.recovery_strategies[error_type]
                recovery_func(error, context)
                logger.info(f"Successfully recovered from {error_type.__name__} in {context}")
                return True
            except Exception as recovery_error:
                logger.error(f"Recovery failed for {error_type.__name__}: {recovery_error}")
                
        return False
        
    def log_error_pattern(self, error: Exception, context: str):
        """Log error patterns for analysis"""
        error_entry = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context
        }
        
        self.error_history.append(error_entry)
        
        # Keep only recent errors (last 100)
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

# Global error recovery manager instance
error_recovery_manager = ErrorRecoveryManager()

def with_progress(total_steps: int, description: str = "Processing..."):
    """Decorator để thêm progress tracking"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracker = ProgressTracker(total_steps, description)
            try:
                # Pass tracker to function if it accepts it
                import inspect
                sig = inspect.signature(func)
                if 'progress_tracker' in sig.parameters:
                    result = func(*args, progress_tracker=tracker, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                tracker.complete()
                return result
            except Exception as e:
                tracker.cleanup()
                raise e
            finally:
                # Auto cleanup after a short delay
                import time
                time.sleep(1)
                tracker.cleanup()
        return wrapper
    return decorator

# Global error handler for uncaught exceptions
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Cho phép Ctrl+C
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical(
        "Uncaught exception", 
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Hiển thị friendly error message trong Streamlit
    if 'streamlit' in str(exc_traceback):
        st.error("❌ Có lỗi nghiêm trọng xảy ra. Vui lòng refresh trang và thử lại.")

# Set global exception handler
import sys
sys.excepthook = global_exception_handler
