"""
Validation functions cho Study Buddy
"""
import re
import os
from typing import Optional, Tuple, List, Dict, Any
from ..config.constants import (
    SUPPORTED_FILE_TYPES, MAX_FILE_SIZE, MIN_FILE_SIZE, MAX_FILE_NAME_LENGTH,
    MAX_MESSAGE_LENGTH, MAX_DOCUMENT_CHARS, ERROR_MESSAGES, PATTERNS,
    MAX_QUESTIONS_COUNT, MIN_QUESTIONS_COUNT, MAX_PDF_DPI, MIN_PDF_DPI
)

class ValidationError(Exception):
    """Custom exception cho validation errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class FileValidator:
    """Validator cho file uploads"""
    
    @staticmethod
    def validate_file(uploaded_file) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Kiểm tra file có tồn tại không
            if not uploaded_file:
                return False, "Không có file được upload"
            
            # Kiểm tra tên file
            if not FileValidator.validate_filename(uploaded_file.name):
                return False, ERROR_MESSAGES['file_name_too_long'].format(
                    max_length=MAX_FILE_NAME_LENGTH
                )
            
            # Kiểm tra kích thước file
            if not FileValidator.validate_file_size(uploaded_file.size):
                if uploaded_file.size > MAX_FILE_SIZE:
                    return False, ERROR_MESSAGES['file_too_large'].format(
                        max_size=MAX_FILE_SIZE // (1024 * 1024)
                    )
                else:
                    return False, ERROR_MESSAGES['file_too_small'].format(
                        min_size=MIN_FILE_SIZE
                    )
            
            # Kiểm tra định dạng file
            if not FileValidator.validate_file_type(uploaded_file.name):
                supported_formats = ', '.join(SUPPORTED_FILE_TYPES.keys())
                return False, ERROR_MESSAGES['unsupported_format'].format(
                    formats=supported_formats
                )
            
            return True, None
            
        except Exception as e:
            return False, f"Lỗi validation file: {str(e)}"
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate tên file"""
        if not filename or len(filename) > MAX_FILE_NAME_LENGTH:
            return False
        
        # Kiểm tra ký tự không hợp lệ
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in filename:
                return False
        
        return True
    
    @staticmethod
    def validate_file_size(size: int) -> bool:
        """Validate kích thước file"""
        return MIN_FILE_SIZE <= size <= MAX_FILE_SIZE
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Validate loại file"""
        if not filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        return extension in SUPPORTED_FILE_TYPES.keys()
    
    @staticmethod
    def get_file_extension(filename: str) -> Optional[str]:
        """Lấy extension của file"""
        if not filename or '.' not in filename:
            return None
        return filename.lower().split('.')[-1]

class MessageValidator:
    """Validator cho chat messages"""
    
    @staticmethod
    def validate_message(message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate chat message
        
        Args:
            message: Nội dung tin nhắn
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Kiểm tra message có tồn tại không
            if not message or not message.strip():
                return False, "Tin nhắn không được để trống"
            
            # Kiểm tra độ dài message
            if len(message) > MAX_MESSAGE_LENGTH:
                return False, ERROR_MESSAGES['message_too_long'].format(
                    max_length=MAX_MESSAGE_LENGTH
                )
            
            # Kiểm tra ký tự đặc biệt hoặc spam
            if MessageValidator.contains_spam_patterns(message):
                return False, "Tin nhắn chứa nội dung không phù hợp"
            
            return True, None
            
        except Exception as e:
            return False, f"Lỗi validation message: {str(e)}"
    
    @staticmethod
    def contains_spam_patterns(message: str) -> bool:
        """Kiểm tra message có chứa spam patterns không"""
        # Danh sách patterns spam đơn giản
        spam_patterns = [
            r'(.)\1{10,}',  # Lặp lại ký tự quá nhiều
            r'[A-Z]{20,}',  # Toàn chữ hoa quá dài
            r'[!@#$%^&*]{5,}',  # Quá nhiều ký tự đặc biệt
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, message):
                return True
        
        return False

class UserValidator:
    """Validator cho user data"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address"""
        if not email or not email.strip():
            return False, "Email không được để trống"
        
        if not re.match(PATTERNS['email'], email.strip()):
            return False, "Định dạng email không hợp lệ"
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """Validate username"""
        if not username or not username.strip():
            return False, "Username không được để trống"
        
        username = username.strip()
        
        if not re.match(PATTERNS['username'], username):
            return False, "Username chỉ được chứa chữ cái, số và dấu gạch dưới (3-20 ký tự)"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """Validate password"""
        if not password:
            return False, "Mật khẩu không được để trống"
        
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự"
        
        if len(password) > 100:
            return False, "Mật khẩu không được quá 100 ký tự"
        
        return True, None

class DocumentValidator:
    """Validator cho document processing"""
    
    @staticmethod
    def validate_document_content(content: str) -> Tuple[bool, Optional[str]]:
        """Validate nội dung document"""
        if not content or not content.strip():
            return False, "Nội dung document trống"
        
        if len(content) > MAX_DOCUMENT_CHARS:
            return False, f"Nội dung document quá dài (tối đa {MAX_DOCUMENT_CHARS:,} ký tự)"
        
        return True, None
    
    @staticmethod
    def validate_page_number(page_num: int, total_pages: int) -> Tuple[bool, Optional[str]]:
        """Validate số trang PDF"""
        if not isinstance(page_num, int) or page_num < 1:
            return False, "Số trang phải là số nguyên dương"
        
        if page_num > total_pages:
            return False, ERROR_MESSAGES['invalid_page_number'].format(
                max_pages=total_pages
            )
        
        return True, None
    
    @staticmethod
    def validate_dpi(dpi: int) -> Tuple[bool, Optional[str]]:
        """Validate DPI cho PDF conversion"""
        if not isinstance(dpi, int):
            return False, "DPI phải là số nguyên"
        
        if not (MIN_PDF_DPI <= dpi <= MAX_PDF_DPI):
            return False, f"DPI phải trong khoảng {MIN_PDF_DPI}-{MAX_PDF_DPI}"
        
        return True, None
    
    @staticmethod
    def validate_questions_list(questions: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate danh sách câu hỏi gợi ý"""
        if not questions:
            return False, "Danh sách câu hỏi trống"
        
        if len(questions) < MIN_QUESTIONS_COUNT:
            return False, f"Phải có ít nhất {MIN_QUESTIONS_COUNT} câu hỏi"
        
        if len(questions) > MAX_QUESTIONS_COUNT:
            return False, f"Không được quá {MAX_QUESTIONS_COUNT} câu hỏi"
        
        # Kiểm tra từng câu hỏi
        for i, question in enumerate(questions):
            if not question or not question.strip():
                return False, f"Câu hỏi thứ {i+1} trống"
            
            if len(question.strip()) < 5:
                return False, f"Câu hỏi thứ {i+1} quá ngắn"
            
            if len(question.strip()) > 200:
                return False, f"Câu hỏi thứ {i+1} quá dài"
        
        return True, None

class SessionValidator:
    """Validator cho chat sessions"""
    
    @staticmethod
    def validate_session_title(title: str) -> Tuple[bool, Optional[str]]:
        """Validate session title"""
        if not title or not title.strip():
            return False, "Tiêu đề session không được để trống"
        
        title = title.strip()
        
        if len(title) > 100:
            return False, "Tiêu đề session không được quá 100 ký tự"
        
        return True, None
    
    @staticmethod
    def validate_user_id(user_id: Any) -> Tuple[bool, Optional[str]]:
        """Validate user ID"""
        if not user_id:
            return False, "User ID không được để trống"
        
        # Convert to string for validation
        user_id_str = str(user_id)
        
        # Kiểm tra UUID format nếu có dấu gạch ngang
        if '-' in user_id_str:
            if not re.match(PATTERNS['uuid'], user_id_str):
                return False, "User ID không đúng định dạng UUID"
        
        return True, None

def safe_execute(func, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Safely execute a function với error handling
    
    Args:
        func: Function to execute
        *args: Arguments for function
        **kwargs: Keyword arguments for function
        
    Returns:
        Tuple[bool, Any, Optional[str]]: (success, result, error_message)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except ValidationError as e:
        return False, None, e.message
    except Exception as e:
        return False, None, f"Lỗi không xác định: {str(e)}"

def validate_all_inputs(data: Dict[str, Any], validators: Dict[str, callable]) -> Dict[str, Any]:
    """
    Validate multiple inputs cùng lúc
    
    Args:
        data: Dict chứa data cần validate
        validators: Dict chứa validator functions cho từng key
        
    Returns:
        Dict chứa validation results
    """
    results = {
        'is_valid': True,
        'errors': {},
        'warnings': []
    }
    
    for key, value in data.items():
        if key in validators:
            validator_func = validators[key]
            is_valid, error_msg = validator_func(value)
            
            if not is_valid:
                results['is_valid'] = False
                results['errors'][key] = error_msg
    
    return results
