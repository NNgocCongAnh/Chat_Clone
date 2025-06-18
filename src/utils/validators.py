"""
Enhanced Validation System for Study Buddy v2.0
Author: Trần Đức Việt - Database & Integration Specialist
Advanced validation with security, performance optimization, and comprehensive error handling
"""
import re
import os
import hashlib
import mimetypes
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass
import logging

from ..config.constants import (
    SUPPORTED_FILE_TYPES, MAX_FILE_SIZE, MIN_FILE_SIZE, MAX_FILE_NAME_LENGTH,
    MAX_MESSAGE_LENGTH, MAX_DOCUMENT_CHARS, ERROR_MESSAGES, PATTERNS,
    MAX_QUESTIONS_COUNT, MIN_QUESTIONS_COUNT, MAX_PDF_DPI, MIN_PDF_DPI
)

# Enhanced Validation System Classes
@dataclass
class ValidationResult:
    """Enhanced validation result với detailed information"""
    is_valid: bool
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

class ValidationError(Exception):
    """Enhanced custom exception cho validation errors"""
    def __init__(self, message: str, error_code: str = None, metadata: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging"""
        return {
            'message': self.message,
            'error_code': self.error_code,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

class SecurityValidator:
    """Enhanced security validation cho file và content"""
    
    # Dangerous file signatures (magic bytes)
    DANGEROUS_SIGNATURES = {
        b'\x4D\x5A': 'executable',  # PE executable
        b'\x7F\x45\x4C\x46': 'elf',  # ELF executable
        b'\xCA\xFE\xBA\xBE': 'java',  # Java class
        b'\x50\x4B\x03\x04': 'zip_based',  # ZIP/DOCX (needs deeper inspection)
    }
    
    # Malicious patterns in content
    MALICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # JavaScript
        r'javascript\s*:',  # JavaScript protocol
        r'vbscript\s*:',   # VBScript protocol
        r'on\w+\s*=',      # Event handlers
        r'eval\s*\(',      # eval function
        r'setTimeout\s*\(',  # setTimeout
        r'setInterval\s*\(',  # setInterval
    ]
    
    @staticmethod
    def scan_file_content(file_content: bytes, filename: str) -> ValidationResult:
        """Enhanced file content security scanning"""
        try:
            # Check file signature
            signature_result = SecurityValidator._check_file_signature(file_content, filename)
            if not signature_result.is_valid:
                return signature_result
            
            # Check file size anomalies
            size_result = SecurityValidator._check_size_anomalies(file_content, filename)
            if not size_result.is_valid:
                return size_result
            
            # Scan for malicious content in text files
            if filename.lower().endswith(('.txt', '.md', '.html', '.xml')):
                content_result = SecurityValidator._scan_text_content(file_content)
                if not content_result.is_valid:
                    return content_result
            
            return ValidationResult(is_valid=True, metadata={'scan_completed': True})
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Security scan failed: {str(e)}",
                error_code="security_scan_error"
            )
    
    @staticmethod
    def _check_file_signature(content: bytes, filename: str) -> ValidationResult:
        """Check file magic bytes for dangerous signatures"""
        if len(content) < 4:
            return ValidationResult(is_valid=True)
        
        file_header = content[:4]
        
        for signature, file_type in SecurityValidator.DANGEROUS_SIGNATURES.items():
            if content.startswith(signature):
                if file_type == 'zip_based' and filename.lower().endswith('.docx'):
                    # DOCX is zip-based, this is normal
                    continue
                    
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Dangerous file type detected: {file_type}",
                    error_code="dangerous_file_signature"
                )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def _check_size_anomalies(content: bytes, filename: str) -> ValidationResult:
        """Check for file size anomalies"""
        file_size = len(content)
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # Size limits per file type
        type_limits = {
            'txt': 50 * 1024 * 1024,   # 50MB for text
            'md': 50 * 1024 * 1024,    # 50MB for markdown
            'pdf': 200 * 1024 * 1024,  # 200MB for PDF
            'docx': 100 * 1024 * 1024, # 100MB for DOCX
        }
        
        if extension in type_limits and file_size > type_limits[extension]:
            return ValidationResult(
                is_valid=False,
                error_message=f"File size exceeds limit for {extension} files",
                error_code="file_size_anomaly"
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def _scan_text_content(content: bytes) -> ValidationResult:
        """Scan text content for malicious patterns"""
        try:
            text_content = content.decode('utf-8', errors='ignore')
            
            for pattern in SecurityValidator.MALICIOUS_PATTERNS:
                if re.search(pattern, text_content, re.IGNORECASE):
                    return ValidationResult(
                        is_valid=False,
                        error_message="Malicious content pattern detected",
                        error_code="malicious_content"
                    )
            
            return ValidationResult(is_valid=True)
            
        except Exception:
            return ValidationResult(is_valid=True)  # If can't decode, assume safe

class FileValidator:
    """Enhanced validator cho file uploads với security scanning"""
    
    @staticmethod
    def validate_file(uploaded_file) -> ValidationResult:
        """
        Enhanced file validation với comprehensive security checks
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            ValidationResult: Enhanced validation result
        """
        try:
            # Kiểm tra file có tồn tại không
            if not uploaded_file:
                return ValidationResult(
                    is_valid=False,
                    error_message="Không có file được upload",
                    error_code="no_file"
                )
            
            # Enhanced filename validation
            filename_result = FileValidator.validate_filename_enhanced(uploaded_file.name)
            if not filename_result.is_valid:
                return filename_result
            
            # Enhanced size validation
            size_result = FileValidator.validate_file_size_enhanced(uploaded_file.size)
            if not size_result.is_valid:
                return size_result
            
            # Enhanced type validation
            type_result = FileValidator.validate_file_type_enhanced(uploaded_file.name)
            if not type_result.is_valid:
                return type_result
            
            # Security scanning
            try:
                file_content = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer
                
                security_result = SecurityValidator.scan_file_content(file_content, uploaded_file.name)
                if not security_result.is_valid:
                    return security_result
                
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Security scan failed: {str(e)}",
                    error_code="security_scan_failed"
                )
            
            # Generate file metadata
            metadata = FileValidator._generate_file_metadata(uploaded_file)
            
            return ValidationResult(
                is_valid=True,
                metadata=metadata
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"File validation error: {str(e)}",
                error_code="validation_error"
            )
    
    @staticmethod
    def validate_filename_enhanced(filename: str) -> ValidationResult:
        """Enhanced filename validation"""
        if not filename:
            return ValidationResult(
                is_valid=False,
                error_message="Tên file không được để trống",
                error_code="empty_filename"
            )
        
        if len(filename) > MAX_FILE_NAME_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=ERROR_MESSAGES['file_name_too_long'].format(
                    max_length=MAX_FILE_NAME_LENGTH
                ),
                error_code="filename_too_long"
            )
        
        # Enhanced character validation
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/', '\0']
        for char in dangerous_chars:
            if char in filename:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Tên file chứa ký tự không hợp lệ: {char}",
                    error_code="invalid_filename_char"
                )
        
        # Check for reserved names
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'LPT1', 'LPT2']
        filename_base = filename.split('.')[0].upper()
        if filename_base in reserved_names:
            return ValidationResult(
                is_valid=False,
                error_message="Tên file không được sử dụng tên hệ thống",
                error_code="reserved_filename"
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_file_size_enhanced(size: int) -> ValidationResult:
        """Enhanced file size validation"""
        if size < MIN_FILE_SIZE:
            return ValidationResult(
                is_valid=False,
                error_message=ERROR_MESSAGES['file_too_small'].format(min_size=MIN_FILE_SIZE),
                error_code="file_too_small"
            )
        
        if size > MAX_FILE_SIZE:
            return ValidationResult(
                is_valid=False,
                error_message=ERROR_MESSAGES['file_too_large'].format(
                    max_size=MAX_FILE_SIZE // (1024 * 1024)
                ),
                error_code="file_too_large"
            )
        
        # Warning for large files
        warnings = []
        if size > 50 * 1024 * 1024:  # 50MB
            warnings.append("File khá lớn, quá trình xử lý có thể mất thời gian")
        
        return ValidationResult(
            is_valid=True,
            warnings=warnings,
            metadata={'size_bytes': size, 'size_mb': round(size / (1024 * 1024), 2)}
        )
    
    @staticmethod
    def validate_file_type_enhanced(filename: str) -> ValidationResult:
        """Enhanced file type validation với MIME type checking"""
        if not filename or '.' not in filename:
            return ValidationResult(
                is_valid=False,
                error_message="File phải có extension",
                error_code="no_extension"
            )
        
        extension = filename.lower().split('.')[-1]
        
        if extension not in SUPPORTED_FILE_TYPES.keys():
            supported_formats = ', '.join(SUPPORTED_FILE_TYPES.keys())
            return ValidationResult(
                is_valid=False,
                error_message=ERROR_MESSAGES['unsupported_format'].format(
                    formats=supported_formats
                ),
                error_code="unsupported_format"
            )
        
        # MIME type validation
        expected_mime = SUPPORTED_FILE_TYPES[extension]
        detected_mime, _ = mimetypes.guess_type(filename)
        
        metadata = {
            'extension': extension,
            'expected_mime': expected_mime,
            'detected_mime': detected_mime
        }
        
        return ValidationResult(is_valid=True, metadata=metadata)
    
    @staticmethod
    def _generate_file_metadata(uploaded_file) -> Dict[str, Any]:
        """Generate comprehensive file metadata"""
        try:
            content = uploaded_file.read()
            uploaded_file.seek(0)
            
            # Generate file hash
            file_hash = hashlib.sha256(content).hexdigest()
            
            return {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'hash': file_hash,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'content_length': len(content)
            }
        except Exception:
            return {'name': uploaded_file.name, 'size': uploaded_file.size}
    
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
