"""
Constants và cấu hình cho Study Buddy
"""

# File types được hỗ trợ
SUPPORTED_FILE_TYPES = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain',
    'md': 'text/markdown'
}

# Giới hạn file
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
MAX_FILE_NAME_LENGTH = 255
MIN_FILE_SIZE = 1  # 1 byte

# Cấu hình chat
MAX_MESSAGE_LENGTH = 10000
MAX_MESSAGES_PER_SESSION = 1000
MAX_CHAT_HISTORY = 50

# Cấu hình document processing
MAX_DOCUMENT_CHARS = 1000000  # 1M chars
MIN_SUMMARY_LENGTH = 50
MAX_SUMMARY_LENGTH = 500
MAX_QUESTIONS_COUNT = 6
MIN_QUESTIONS_COUNT = 3

# OCR settings
DEFAULT_PDF_DPI = 150
MAX_PDF_DPI = 300
MIN_PDF_DPI = 72

# Database settings
MAX_SESSION_TITLE_LENGTH = 100
MAX_CONTENT_LENGTH = 50000
DB_TIMEOUT = 30  # seconds

# Enhanced LLM settings với advanced configurations
LOCAL_LLM_DEFAULT_URL = "http://localhost:1234/v1"
MAX_LLM_TOKENS = 2000
DEFAULT_TEMPERATURE = 0.7
MAX_CONTEXT_LENGTH = 4000

# Advanced LLM parameters
LLM_GENERATION_CONFIG = {
    'chat': {
        'temperature': 0.6,
        'top_p': 0.9,
        'max_tokens': 1200,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.1
    },
    'document_qa': {
        'temperature': 0.15,
        'top_p': 0.8,
        'max_tokens': 600,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0
    },
    'summarization': {
        'temperature': 0.3,
        'top_p': 0.85,
        'max_tokens': 400,
        'frequency_penalty': 0.2,
        'presence_penalty': 0.1
    }
}

# Smart retry configurations
RETRY_CONFIG = {
    'llm_operations': {
        'max_retries': 2,
        'base_delay': 1.0,
        'backoff_factor': 1.5,
        'rate_limit_delay': 2.0
    },
    'file_processing': {
        'max_retries': 3,
        'base_delay': 0.5,
        'backoff_factor': 2.0,
        'rate_limit_delay': 1.0
    },
    'database_operations': {
        'max_retries': 3,
        'base_delay': 0.3,
        'backoff_factor': 1.2,
        'rate_limit_delay': 0.5
    }
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    'context_management': {
        'max_history_messages': 12,
        'relevant_context_length': 2000,
        'smart_filtering_enabled': True,
        'context_compression_ratio': 0.7
    },
    'document_processing': {
        'chunk_size': 1000,
        'chunk_overlap': 200,
        'batch_processing_size': 3,
        'parallel_processing': False,
        'smart_chunking': True
    },
    'caching': {
        'enable_response_cache': True,
        'enable_document_cache': True,
        'cache_ttl_minutes': 60,
        'max_cache_items': 100
    }
}

# Enhanced error messages với context-aware messaging
ERROR_MESSAGES = {
    # File processing errors
    'file_too_large': 'File quá lớn. Kích thước tối đa là {max_size}MB.',
    'file_too_small': 'File quá nhỏ. Kích thước tối thiểu là {min_size} bytes.',
    'unsupported_format': 'Định dạng file không được hỗ trợ. Chỉ hỗ trợ: {formats}.',
    'file_name_too_long': 'Tên file quá dài. Tối đa {max_length} ký tự.',
    'upload_failed': 'Upload file thất bại. Vui lòng thử lại.',
    'processing_failed': 'Xử lý tài liệu thất bại. Vui lòng kiểm tra file.',
    'file_corrupted': 'File bị lỗi hoặc không đầy đủ. Vui lòng kiểm tra và upload lại.',
    
    # OCR and document processing
    'ocr_failed': 'OCR PDF thất bại. File có thể bị lỗi hoặc không có text.',
    'pdf_password_protected': 'PDF được bảo vệ bởi mật khẩu. Vui lòng mở khóa trước khi upload.',
    'pdf_no_text': 'PDF không chứa text có thể đọc được.',
    'document_too_long': 'Tài liệu quá dài để xử lý. Vui lòng chia nhỏ hoặc chọn phần cần thiết.',
    
    # LLM connection errors với detailed guidance
    'llm_connection_failed': 'Không thể kết nối Local LLM. Kiểm tra LM Studio đang chạy.',
    'llm_model_not_loaded': 'Local LLM chưa load model. Vui lòng khởi động LM Studio và load model.',
    'llm_connection_timeout': 'Kết nối Local LLM timeout. Model có thể quá lớn cho hệ thống.',
    'llm_generation_failed': 'LLM không thể tạo phản hồi. Thử với câu hỏi đơn giản hơn.',
    'llm_context_overflow': 'Nội dung quá dài cho LLM xử lý. Vui lòng rút gọn câu hỏi.',
    'llm_server_overloaded': 'LLM server đang quá tải. Vui lòng chờ và thử lại.',
    
    # Database errors
    'database_connection_failed': 'Lỗi kết nối database. Vui lòng thử lại.',
    'session_create_failed': 'Không thể tạo session chat mới.',
    'message_save_failed': 'Không thể lưu tin nhắn.',
    'data_corruption': 'Dữ liệu bị lỗi. Vui lòng khởi tạo lại session.',
    'storage_full': 'Dung lượng lưu trữ đã đầy. Vui lòng xóa dữ liệu cũ.',
    
    # Authentication and session
    'authentication_required': 'Vui lòng đăng nhập để sử dụng tính năng này.',
    'invalid_session': 'Session không hợp lệ hoặc đã hết hạn.',
    'session_expired': 'Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.',
    'unauthorized_access': 'Không có quyền truy cập tài nguyên này.',
    
    # Input validation
    'message_too_long': 'Tin nhắn quá dài. Tối đa {max_length} ký tự.',
    'too_many_messages': 'Quá nhiều tin nhắn trong session. Tối đa {max_count} tin nhắn.',
    'invalid_page_number': 'Số trang không hợp lệ. Phải từ 1 đến {max_pages}.',
    'empty_input': 'Vui lòng nhập nội dung trước khi gửi.',
    'invalid_format': 'Định dạng dữ liệu không hợp lệ.',
    
    # Network and API errors
    'network_error': 'Lỗi kết nối mạng. Vui lòng kiểm tra internet.',
    'timeout_error': 'Thao tác timeout. Vui lòng thử lại.',
    'api_rate_limit': 'API đã vượt giới hạn rate limit. Vui lòng chờ và thử lại.',
    'service_unavailable': 'Dịch vụ tạm thời không khả dụng. Vui lòng thử lại sau.',
    'mistral_api_limit': 'Mistral API đã vượt giới hạn. Vui lòng thử lại sau.',
    'mistral_api_auth': 'Mistral API key không hợp lệ. Kiểm tra cấu hình.',
    
    # System errors
    'permission_denied': 'Không có quyền thực hiện thao tác này.',
    'resource_not_found': 'Không tìm thấy tài nguyên được yêu cầu.',
    'system_overload': 'Hệ thống đang quá tải. Vui lòng thử lại sau.',
    'maintenance_mode': 'Hệ thống đang bảo trì. Vui lòng quay lại sau.',
    'unexpected_error': 'Lỗi không mong muốn. Vui lòng báo cáo cho admin.'
}

# Success messages
SUCCESS_MESSAGES = {
    'file_uploaded': 'Upload file thành công: {filename}',
    'document_processed': 'Xử lý tài liệu thành công',
    'session_created': 'Tạo cuộc trò chuyện mới thành công',
    'message_sent': 'Gửi tin nhắn thành công',
    'login_success': 'Đăng nhập thành công',
    'logout_success': 'Đăng xuất thành công',
    'account_created': 'Tạo tài khoản thành công',
    'session_deleted': 'Xóa cuộc trò chuyện thành công',
    'document_deleted': 'Xóa tài liệu thành công'
}

# Warning messages
WARNING_MESSAGES = {
    'large_file': 'File khá lớn, việc xử lý có thể mất thời gian.',
    'many_pages': 'PDF có nhiều trang, OCR có thể chậm.',
    'llm_offline': 'LLM offline, chạy ở chế độ demo.',
    'no_internet': 'Không có kết nối internet.',
    'beta_feature': 'Đây là tính năng beta, có thể không ổn định.',
    'data_loss': 'Dữ liệu có thể bị mất nếu không lưu.',
    'session_limit': 'Gần đạt giới hạn số session.',
    'storage_limit': 'Dung lượng lưu trữ gần hết.'
}

# Regex patterns
PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'username': r'^[a-zA-Z0-9_]{3,20}$',
    'filename': r'^[a-zA-Z0-9._-]+$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
}

# Default values
DEFAULTS = {
    'chat_title': 'Cuộc trò chuyện mới',
    'user_avatar': '👤',
    'assistant_avatar': '🤖',
    'session_timeout': 3600,  # 1 hour
    'auto_save_interval': 30,  # 30 seconds
    'max_retry_attempts': 3,
    'retry_delay': 1.0  # seconds
}

# Enhanced feature flags với granular control
FEATURES = {
    # Core features
    'enable_ocr': True,
    'enable_rag': True,
    'enable_chat_export': True,
    'enable_document_cache': True,
    'enable_session_persistence': True,
    'enable_auto_save': True,
    'enable_offline_mode': True,
    
    # Advanced features
    'enable_smart_context_management': True,
    'enable_intelligent_retry': True,
    'enable_adaptive_chunking': True,
    'enable_response_caching': True,
    'enable_error_recovery': True,
    'enable_performance_monitoring': True,
    'enable_progressive_loading': True,
    'enable_context_compression': True,
    
    # UI/UX enhancements
    'enable_progress_tracking': True,
    'enable_eta_calculation': True,
    'enable_smart_suggestions': True,
    'enable_typing_indicators': True,
    'enable_message_reactions': False,
    
    # Development and debugging
    'enable_debug_mode': False,
    'enable_telemetry': False,
    'enable_performance_profiling': False,
    'enable_error_reporting': True,
    'enable_usage_analytics': False,
    
    # Experimental features
    'enable_multi_model_support': False,
    'enable_voice_input': False,
    'enable_real_time_collaboration': False,
    'enable_advanced_search': False
}

# Model-specific configurations
MODEL_CONFIGS = {
    'llama': {
        'recommended_params': {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 1000
        },
        'context_window': 4096,
        'best_use_cases': ['general_chat', 'code_assistance']
    },
    'mistral': {
        'recommended_params': {
            'temperature': 0.6,
            'top_p': 0.85,
            'max_tokens': 1200
        },
        'context_window': 8192,
        'best_use_cases': ['document_qa', 'summarization']
    },
    'phi': {
        'recommended_params': {
            'temperature': 0.5,
            'top_p': 0.8,
            'max_tokens': 800
        },
        'context_window': 2048,
        'best_use_cases': ['quick_responses', 'mobile_deployment']
    }
}

# API endpoints (nếu có external APIs)
API_ENDPOINTS = {
    'mistral_ocr': 'https://api.mistral.ai/v1/ocr',
    'local_llm': LOCAL_LLM_DEFAULT_URL,
    'supabase': '',  # Sẽ được set từ environment
}

# Cache settings
CACHE_SETTINGS = {
    'ttl': 3600,  # 1 hour
    'max_size': 100,  # số items
    'cleanup_interval': 300  # 5 minutes
}
