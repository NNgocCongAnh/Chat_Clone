"""
Unit tests cho validators module
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.validators import (
    FileValidator, MessageValidator, UserValidator, 
    DocumentValidator, SessionValidator, ValidationError
)

class MockUploadedFile:
    """Mock UploadedFile cho testing"""
    def __init__(self, name, size):
        self.name = name
        self.size = size

class TestFileValidator:
    """Test FileValidator class"""
    
    def test_validate_filename_valid(self):
        """Test valid filenames"""
        assert FileValidator.validate_filename("document.pdf") == True
        assert FileValidator.validate_filename("test_file.docx") == True
        assert FileValidator.validate_filename("notes.txt") == True
    
    def test_validate_filename_invalid(self):
        """Test invalid filenames"""
        assert FileValidator.validate_filename("") == False
        assert FileValidator.validate_filename("file<name>.pdf") == False
        assert FileValidator.validate_filename("file|name.txt") == False
        assert FileValidator.validate_filename("a" * 300 + ".pdf") == False
    
    def test_validate_file_size(self):
        """Test file size validation"""
        assert FileValidator.validate_file_size(1024) == True  # 1KB
        assert FileValidator.validate_file_size(50 * 1024 * 1024) == True  # 50MB
        assert FileValidator.validate_file_size(0) == False  # 0 bytes
        assert FileValidator.validate_file_size(300 * 1024 * 1024) == False  # 300MB
    
    def test_validate_file_type(self):
        """Test file type validation"""
        assert FileValidator.validate_file_type("document.pdf") == True
        assert FileValidator.validate_file_type("text.txt") == True
        assert FileValidator.validate_file_type("notes.md") == True
        assert FileValidator.validate_file_type("document.docx") == True
        assert FileValidator.validate_file_type("image.jpg") == False
        assert FileValidator.validate_file_type("archive.zip") == False
    
    def test_validate_file_complete(self):
        """Test complete file validation"""
        # Valid file
        valid_file = MockUploadedFile("test.pdf", 1024 * 1024)  # 1MB
        is_valid, error = FileValidator.validate_file(valid_file)
        assert is_valid == True
        assert error is None
        
        # Invalid file - too large
        large_file = MockUploadedFile("large.pdf", 300 * 1024 * 1024)  # 300MB
        is_valid, error = FileValidator.validate_file(large_file)
        assert is_valid == False
        assert "quá lớn" in error
        
        # Invalid file - unsupported type
        invalid_file = MockUploadedFile("image.jpg", 1024)
        is_valid, error = FileValidator.validate_file(invalid_file)
        assert is_valid == False
        assert "không được hỗ trợ" in error

class TestMessageValidator:
    """Test MessageValidator class"""
    
    def test_validate_message_valid(self):
        """Test valid messages"""
        is_valid, error = MessageValidator.validate_message("Hello world")
        assert is_valid == True
        assert error is None
        
        is_valid, error = MessageValidator.validate_message("Xin chào, tôi có câu hỏi về tài liệu này.")
        assert is_valid == True
        assert error is None
    
    def test_validate_message_invalid(self):
        """Test invalid messages"""
        # Empty message
        is_valid, error = MessageValidator.validate_message("")
        assert is_valid == False
        assert "trống" in error
        
        # Too long message
        long_message = "a" * 15000
        is_valid, error = MessageValidator.validate_message(long_message)
        assert is_valid == False
        assert "quá dài" in error
    
    def test_spam_detection(self):
        """Test spam pattern detection"""
        # Repeated characters
        spam_msg = "aaaaaaaaaaaaaaaaaaa"
        assert MessageValidator.contains_spam_patterns(spam_msg) == True
        
        # Too many caps
        caps_msg = "HELLO THIS IS ALL CAPS MESSAGE FOR TESTING"
        assert MessageValidator.contains_spam_patterns(caps_msg) == True
        
        # Normal message
        normal_msg = "This is a normal message"
        assert MessageValidator.contains_spam_patterns(normal_msg) == False

class TestUserValidator:
    """Test UserValidator class"""
    
    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        assert UserValidator.validate_email("user@example.com")[0] == True
        assert UserValidator.validate_email("test.email@domain.co.uk")[0] == True
        
        # Invalid emails
        assert UserValidator.validate_email("invalid-email")[0] == False
        assert UserValidator.validate_email("@domain.com")[0] == False
        assert UserValidator.validate_email("user@")[0] == False
        assert UserValidator.validate_email("")[0] == False
    
    def test_validate_username(self):
        """Test username validation"""
        # Valid usernames
        assert UserValidator.validate_username("user123")[0] == True
        assert UserValidator.validate_username("test_user")[0] == True
        
        # Invalid usernames
        assert UserValidator.validate_username("ab")[0] == False  # Too short
        assert UserValidator.validate_username("a" * 25)[0] == False  # Too long
        assert UserValidator.validate_username("user@name")[0] == False  # Invalid chars
        assert UserValidator.validate_username("")[0] == False  # Empty
    
    def test_validate_password(self):
        """Test password validation"""
        # Valid passwords
        assert UserValidator.validate_password("password123")[0] == True
        assert UserValidator.validate_password("mySecurePass")[0] == True
        
        # Invalid passwords
        assert UserValidator.validate_password("12345")[0] == False  # Too short
        assert UserValidator.validate_password("")[0] == False  # Empty
        assert UserValidator.validate_password("a" * 150)[0] == False  # Too long

class TestDocumentValidator:
    """Test DocumentValidator class"""
    
    def test_validate_document_content(self):
        """Test document content validation"""
        # Valid content
        content = "This is a sample document content with sufficient length."
        assert DocumentValidator.validate_document_content(content)[0] == True
        
        # Empty content
        assert DocumentValidator.validate_document_content("")[0] == False
        assert DocumentValidator.validate_document_content("   ")[0] == False
        
        # Too long content
        long_content = "a" * 2000000  # 2M chars
        assert DocumentValidator.validate_document_content(long_content)[0] == False
    
    def test_validate_page_number(self):
        """Test page number validation"""
        # Valid page numbers
        assert DocumentValidator.validate_page_number(1, 10)[0] == True
        assert DocumentValidator.validate_page_number(5, 10)[0] == True
        assert DocumentValidator.validate_page_number(10, 10)[0] == True
        
        # Invalid page numbers
        assert DocumentValidator.validate_page_number(0, 10)[0] == False
        assert DocumentValidator.validate_page_number(11, 10)[0] == False
        assert DocumentValidator.validate_page_number(-1, 10)[0] == False
    
    def test_validate_questions_list(self):
        """Test questions list validation"""
        # Valid questions
        valid_questions = [
            "What is the main topic?",
            "How does this work?",
            "What are the benefits?"
        ]
        assert DocumentValidator.validate_questions_list(valid_questions)[0] == True
        
        # Too few questions
        few_questions = ["Only one question?"]
        assert DocumentValidator.validate_questions_list(few_questions)[0] == False
        
        # Too many questions
        many_questions = ["Question " + str(i) for i in range(10)]
        assert DocumentValidator.validate_questions_list(many_questions)[0] == False
        
        # Empty questions
        empty_questions = ["", "Valid question", ""]
        assert DocumentValidator.validate_questions_list(empty_questions)[0] == False

class TestSessionValidator:
    """Test SessionValidator class"""
    
    def test_validate_session_title(self):
        """Test session title validation"""
        # Valid titles
        assert SessionValidator.validate_session_title("My Chat Session")[0] == True
        assert SessionValidator.validate_session_title("Document Discussion")[0] == True
        
        # Invalid titles
        assert SessionValidator.validate_session_title("")[0] == False
        assert SessionValidator.validate_session_title("   ")[0] == False
        assert SessionValidator.validate_session_title("a" * 150)[0] == False  # Too long
    
    def test_validate_user_id(self):
        """Test user ID validation"""
        # Valid UUIDs
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        assert SessionValidator.validate_user_id(valid_uuid)[0] == True
        
        # Valid integer IDs
        assert SessionValidator.validate_user_id("12345")[0] == True
        assert SessionValidator.validate_user_id(12345)[0] == True
        
        # Invalid IDs
        assert SessionValidator.validate_user_id("")[0] == False
        assert SessionValidator.validate_user_id(None)[0] == False

def run_tests():
    """Run all tests manually"""
    test_classes = [
        TestFileValidator(),
        TestMessageValidator(), 
        TestUserValidator(),
        TestDocumentValidator(),
        TestSessionValidator()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n🧪 Running {class_name}...")
        
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    method = getattr(test_class, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                    passed_tests += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {str(e)}")
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
