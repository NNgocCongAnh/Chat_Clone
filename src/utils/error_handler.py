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
    Execute function với retry mechanism
    
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
    
    for attempt in range(max_retries + 1):
        try:
            result = func()
            return True, result, None
            
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"{context} - Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 1.5  # Exponential backoff
            else:
                error_message = handle_error(e, context, show_user)
                return False, None, error_message
    
    return False, None, "Max retries exceeded"

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
    """Class để track progress của long-running operations"""
    
    def __init__(self, total_steps: int, description: str = "Processing..."):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        
    def update(self, step_description: str = ""):
        """Update progress"""
        self.current_step += 1
        progress = self.current_step / self.total_steps
        
        self.progress_bar.progress(progress)
        
        if step_description:
            self.status_text.text(f"{self.description} - {step_description} ({self.current_step}/{self.total_steps})")
        else:
            self.status_text.text(f"{self.description} ({self.current_step}/{self.total_steps})")
    
    def complete(self, final_message: str = "Hoàn thành!"):
        """Complete progress tracking"""
        self.progress_bar.progress(1.0)
        self.status_text.text(final_message)
        
    def cleanup(self):
        """Clean up progress elements"""
        try:
            self.progress_bar.empty()
            self.status_text.empty()
        except:
            pass

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
