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

# LLM settings
LOCAL_LLM_DEFAULT_URL = "http://localhost:1234/v1"
MAX_LLM_TOKENS = 2000
DEFAULT_TEMPERATURE = 0.7
MAX_CONTEXT_LENGTH = 4000

# Error messages
ERROR_MESSAGES = {
    'file_too_large': 'File quá lớn. Kích thước tối đa là {max_size}MB.',
    'file_too_small': 'File quá nhỏ. Kích thước tối thiểu là {min_size} bytes.',
    'unsupported_format': 'Định dạng file không được hỗ trợ. Chỉ hỗ trợ: {formats}.',
    'file_name_too_long': 'Tên file quá dài. Tối đa {max_length} ký tự.',
    'upload_failed': 'Upload file thất bại. Vui lòng thử lại.',
    'processing_failed': 'Xử lý tài liệu thất bại. Vui lòng kiểm tra file.',
    'ocr_failed': 'OCR PDF thất bại. File có thể bị lỗi hoặc không có text.',
    'llm_connection_failed': 'Không thể kết nối LLM. Kiểm tra LM Studio.',
    'database_connection_failed': 'Lỗi kết nối database. Vui lòng thử lại.',
    'session_create_failed': 'Không thể tạo session chat mới.',
    'message_save_failed': 'Không thể lưu tin nhắn.',
    'authentication_required': 'Vui lòng đăng nhập để sử dụng tính năng này.',
    'invalid_session': 'Session không hợp lệ hoặc đã hết hạn.',
    'message_too_long': 'Tin nhắn quá dài. Tối đa {max_length} ký tự.',
    'too_many_messages': 'Quá nhiều tin nhắn trong session. Tối đa {max_count} tin nhắn.',
    'invalid_page_number': 'Số trang không hợp lệ. Phải từ 1 đến {max_pages}.',
    'pdf_page_extract_failed': 'Không thể trích xuất trang PDF.',
    'network_error': 'Lỗi kết nối mạng. Vui lòng kiểm tra internet.',
    'timeout_error': 'Thao tác timeout. Vui lòng thử lại.',
    'permission_denied': 'Không có quyền thực hiện thao tác này.',
    'resource_not_found': 'Không tìm thấy tài nguyên được yêu cầu.'
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

# Feature flags
FEATURES = {
    'enable_ocr': True,
    'enable_rag': True,
    'enable_chat_export': True,
    'enable_document_cache': True,
    'enable_session_persistence': True,
    'enable_auto_save': True,
    'enable_offline_mode': True,
    'enable_debug_mode': False,
    'enable_telemetry': False
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
