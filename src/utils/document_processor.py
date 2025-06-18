import docx
import streamlit as st
from io import BytesIO
import base64
from mistralai import Mistral
import openai
import os
from typing import Dict, Optional, List, Tuple
import fitz  # PyMuPDF
from PIL import Image
from .validators import FileValidator, DocumentValidator
from .error_handler import (
    handle_error, error_boundary, FileProcessingError, 
    LLMConnectionError, show_warning_message, ProgressTracker,
    with_progress, safe_execute_with_retry
)
from ..config.constants import (
    MAX_DOCUMENT_CHARS, DEFAULT_PDF_DPI, MAX_PDF_DPI, MIN_PDF_DPI,
    WARNING_MESSAGES, ERROR_MESSAGES
)

class DocumentProcessor:
    def __init__(self):
        # Khởi tạo Mistral client
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not self.mistral_api_key:
            try:
                self.mistral_api_key = st.secrets.get("MISTRAL_API_KEY", "")
            except Exception:
                self.mistral_api_key = ""
        
        if self.mistral_api_key:
            self.mistral_client = Mistral(api_key=self.mistral_api_key)
        else:
            self.mistral_client = None
            st.warning("⚠️ Chưa cấu hình Mistral API Key. Chức năng OCR PDF sẽ bị hạn chế.")
        
        # Khởi tạo Local LLM client (LM Studio)
        self.local_llm_url = os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1")
        try:
            self.openai_client = openai.OpenAI(
                base_url=self.local_llm_url,
                api_key="not_needed"
            )
            st.success("✅ Đã kết nối Local LLM (LM Studio)")
        except Exception as e:
            self.openai_client = None
            st.warning(f"⚠️ Không thể kết nối Local LLM: {str(e)}. Đảm bảo LM Studio đang chạy trên {self.local_llm_url}")
        
        self.embeddings_cache = {}
    
    @error_boundary("Document processing", show_user=True)
    def process_document(self, uploaded_file) -> Optional[str]:
        """
        Xử lý và trích xuất text từ tài liệu đã upload với validation và error handling
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Extracted text content hoặc None nếu lỗi
        """
        # Validate file trước khi xử lý
        validation_result = FileValidator.validate_file(uploaded_file)
        if not validation_result.is_valid:
            raise FileProcessingError(validation_result.error_message, "file_validation_failed")
        
        # Check file size warning
        if uploaded_file.size > 50 * 1024 * 1024:  # 50MB
            show_warning_message('large_file')
        
        file_extension = FileValidator.get_file_extension(uploaded_file.name)
        if not file_extension:
            raise FileProcessingError("Không thể xác định định dạng file", "unknown_format")
        
        # Progress tracking cho các loại file khác nhau
        if file_extension == 'pdf':
            return self._process_pdf_with_progress(uploaded_file)
        elif file_extension == 'docx':
            return self._process_docx_safe(uploaded_file)
        elif file_extension in ['txt', 'md']:
            return self._process_text_safe(uploaded_file)
        else:
            raise FileProcessingError(
                f"Định dạng file {file_extension} không được hỗ trợ", 
                "unsupported_format"
            )
    
    @with_progress(3, "Xử lý file PDF")
    def _process_pdf_with_progress(self, uploaded_file, progress_tracker=None) -> Optional[str]:
        """Xử lý PDF với progress tracking"""
        if progress_tracker:
            progress_tracker.update("Kiểm tra file PDF")
        
        # Check PDF page count first
        page_count = self.get_pdf_page_count_with_pymupdf(uploaded_file)
        if page_count > 50:
            show_warning_message('many_pages')
        
        if progress_tracker:
            progress_tracker.update("Thực hiện OCR")
        
        content = self.extract_pdf_content(uploaded_file)
        
        if progress_tracker:
            progress_tracker.update("Kiểm tra kết quả")
        
        if content:
            # Validate content length
            is_valid_content, content_error = DocumentValidator.validate_document_content(content)
            if not is_valid_content:
                raise FileProcessingError(content_error, "content_validation_failed")
        
        return content
    
    @error_boundary("DOCX processing", show_user=True)
    def _process_docx_safe(self, uploaded_file) -> Optional[str]:
        """Xử lý DOCX với error handling"""
        try:
            with st.spinner("Đang xử lý file DOCX..."):
                content = self.extract_docx_content(uploaded_file)
                
                if content:
                    # Validate content
                    is_valid, error_msg = DocumentValidator.validate_document_content(content)
                    if not is_valid:
                        raise FileProcessingError(error_msg, "content_validation_failed")
                
                return content
        except Exception as e:
            raise FileProcessingError(f"Lỗi xử lý DOCX: {str(e)}", "docx_processing_failed")
    
    @error_boundary("Text processing", show_user=True)
    def _process_text_safe(self, uploaded_file) -> Optional[str]:
        """Xử lý text file với error handling"""
        try:
            with st.spinner("Đang đọc file text..."):
                content = self.extract_text_content(uploaded_file)
                
                if content:
                    # Validate content
                    is_valid, error_msg = DocumentValidator.validate_document_content(content)
                    if not is_valid:
                        raise FileProcessingError(error_msg, "content_validation_failed")
                
                return content
        except Exception as e:
            raise FileProcessingError(f"Lỗi xử lý text file: {str(e)}", "text_processing_failed")
    
    def extract_pdf_content(self, uploaded_file):
        """Trích xuất text từ file PDF sử dụng Mistral OCR"""
        if not self.mistral_client:
            st.error("Mistral API Key chưa được cấu hình. Không thể xử lý PDF.")
            return None
            
        try:
            # Mã hóa PDF thành base64
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Gọi Mistral OCR API
            with st.spinner("Đang xử lý PDF bằng Mistral OCR..."):
                ocr_response = self.mistral_client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{base64_pdf}"
                    }
                )
                
                # Lưu thông tin từng trang vào cache
                self.pdf_pages_cache = {}
                
                # Trích xuất nội dung từ tất cả các trang
                content = ""
                for i, page in enumerate(ocr_response.pages):
                    if hasattr(page, 'markdown') and page.markdown:
                        page_content = page.markdown.strip()
                        content += page_content + "\n\n"
                        # Cache nội dung từng trang
                        self.pdf_pages_cache[i + 1] = page_content
                
                return content.strip() if content else None
                
        except Exception as e:
            st.error(f"Lỗi khi xử lý PDF với Mistral OCR: {str(e)}")
            return None
    
    def get_pdf_page_count(self, uploaded_file) -> int:
        """
        Lấy số trang của file PDF
        
        Args:
            uploaded_file: File PDF đã upload
            
        Returns:
            Số trang của PDF
        """
        if not self.mistral_client:
            st.error("Mistral API Key chưa được cấu hình.")
            return 0
            
        try:
            # Nếu đã có cache từ lần xử lý trước
            if hasattr(self, 'pdf_pages_cache') and self.pdf_pages_cache:
                return len(self.pdf_pages_cache)
            
            # Mã hóa PDF thành base64
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Gọi Mistral OCR API để lấy thông tin trang
            ocr_response = self.mistral_client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}"
                }
            )
            
            return len(ocr_response.pages) if ocr_response.pages else 0
            
        except Exception as e:
            st.error(f"Lỗi khi đếm trang PDF: {str(e)}")
            return 0
    
    def extract_specific_pdf_page(self, uploaded_file, page_number: int) -> Optional[str]:
        """
        Trích xuất nội dung từ một trang cụ thể của PDF
        
        Args:
            uploaded_file: File PDF đã upload
            page_number: Số trang cần trích xuất (bắt đầu từ 1)
            
        Returns:
            Nội dung của trang đó hoặc None nếu lỗi
        """
        if not self.mistral_client:
            st.error("Mistral API Key chưa được cấu hình.")
            return None
            
        try:
            # Kiểm tra cache trước
            if hasattr(self, 'pdf_pages_cache') and page_number in self.pdf_pages_cache:
                return self.pdf_pages_cache[page_number]
            
            # Mã hóa PDF thành base64
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Gọi Mistral OCR API
            with st.spinner(f"Đang xử lý trang {page_number}..."):
                ocr_response = self.mistral_client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{base64_pdf}"
                    }
                )
                
                # Lấy nội dung trang cụ thể
                if ocr_response.pages and len(ocr_response.pages) >= page_number:
                    page = ocr_response.pages[page_number - 1]  # Index từ 0
                    if hasattr(page, 'markdown') and page.markdown:
                        return page.markdown.strip()
                
                return None
                
        except Exception as e:
            st.error(f"Lỗi khi xử lý trang {page_number}: {str(e)}")
            return None
    
    def extract_pdf_pages_range(self, uploaded_file, start_page: int, end_page: int) -> Dict[int, str]:
        """
        Trích xuất nội dung từ một dải trang của PDF
        
        Args:
            uploaded_file: File PDF đã upload
            start_page: Trang bắt đầu (từ 1)
            end_page: Trang kết thúc (bao gồm)
            
        Returns:
            Dict với key là số trang, value là nội dung
        """
        if not self.mistral_client:
            st.error("Mistral API Key chưa được cấu hình.")
            return {}
            
        try:
            # Mã hóa PDF thành base64
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Gọi Mistral OCR API
            with st.spinner(f"Đang xử lý trang {start_page}-{end_page}..."):
                ocr_response = self.mistral_client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{base64_pdf}"
                    }
                )
                
                # Trích xuất nội dung từ dải trang
                pages_content = {}
                if ocr_response.pages:
                    for page_num in range(start_page, min(end_page + 1, len(ocr_response.pages) + 1)):
                        page_index = page_num - 1  # Index từ 0
                        if page_index < len(ocr_response.pages):
                            page = ocr_response.pages[page_index]
                            if hasattr(page, 'markdown') and page.markdown:
                                pages_content[page_num] = page.markdown.strip()
                
                return pages_content
                
        except Exception as e:
            st.error(f"Lỗi khi xử lý trang {start_page}-{end_page}: {str(e)}")
            return {}
    
    def extract_docx_content(self, uploaded_file):
        """Trích xuất text từ file DOCX"""
        try:
            doc = docx.Document(BytesIO(uploaded_file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"Không thể đọc file DOCX: {str(e)}")
            return None
    
    def extract_text_content(self, uploaded_file):
        """Trích xuất text từ file TXT/MD"""
        try:
            # Thử nhiều encoding
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    content = uploaded_file.read().decode(encoding)
                    return content
                except UnicodeDecodeError:
                    continue
            
            # Nếu tất cả encoding đều thất bại
            st.error("Không thể đọc file text với encoding phù hợp")
            return None
            
        except Exception as e:
            st.error(f"Không thể đọc file text: {str(e)}")
            return None
    
    def chunk_text(self, text, chunk_size=1000, overlap=200):
        """Chia text thành các chunks nhỏ hơn để xử lý"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Tìm điểm ngắt tự nhiên (kết thúc câu hoặc đoạn)
            if end < text_length:
                # Tìm ngắt câu gần nhất
                for i in range(end, start + chunk_size - 100, -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end > overlap else end
        
        return chunks
    
    def summarize_text_with_openai(self, text, max_words=150):
        """Tóm tắt văn bản sử dụng Local LLM"""
        if not self.openai_client:
            return "Không thể kết nối Local LLM. Vui lòng khởi động LM Studio trước."
            
        try:
            # Chia text thành chunks nếu quá dài (GPT có giới hạn token)
            max_input_length = 3000  # Khoảng 3000 characters ~ 750 tokens
            
            if len(text) > max_input_length:
                chunks = self.chunk_text(text, chunk_size=max_input_length, overlap=200)
                summaries = []
                
                # Tóm tắt từng chunk
                for i, chunk in enumerate(chunks[:4]):  # Giới hạn 4 chunks để tránh cost quá cao
                    if len(chunk.strip()) > 100:
                        chunk_summary = self._summarize_chunk_with_openai(chunk, max_words//len(chunks))
                        if chunk_summary:
                            summaries.append(chunk_summary)
                
                # Kết hợp và tóm tắt final
                combined_text = " ".join(summaries)
                if len(combined_text) > max_input_length:
                    final_summary = self._summarize_chunk_with_openai(combined_text, max_words)
                    return final_summary
                else:
                    return combined_text
            else:
                return self._summarize_chunk_with_openai(text, max_words)
                
        except Exception as e:
            st.error(f"Lỗi khi tóm tắt với OpenAI: {str(e)}")
            return f"Không thể tóm tắt tài liệu. Lỗi: {str(e)}"
    
    def _summarize_chunk_with_openai(self, text, max_words=150):
        """Tóm tắt một chunk text bằng Local LLM với improved error handling"""
        
        def _call_summarize_llm():
            prompt = f"""Hãy tóm tắt nội dung sau bằng tiếng Việt, khoảng {max_words} từ. Tập trung vào những ý chính và thông tin quan trọng nhất:

{text}

Tóm tắt ngắn gọn, dễ hiểu:"""

            response = self.openai_client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên gia tóm tắt văn bản. Hãy tóm tắt nội dung một cách súc tích và chính xác bằng tiếng Việt."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3,  # Thấp để có kết quả ổn định
            )
            
            return response.choices[0].message.content.strip()
        
        # Sử dụng safe_execute_with_retry
        success, result, error_message = safe_execute_with_retry(
            _call_summarize_llm,
            max_retries=1,
            delay=0.5,
            context="Local LLM Summarization",
            show_user=False
        )
        
        if success:
            return result
        else:
            # Fallback summary
            return f"📄 **Tóm tắt tự động:** Tài liệu chứa {len(text)} ký tự. Nội dung bao gồm các thông tin quan trọng cần được phân tích chi tiết. (Local LLM không khả dụng - {str(error_message)[:50]}...)"
    
    # Để tương thích backward, tạo alias
    def summarize_text(self, text, max_length=200, min_length=50):
        """Alias cho backward compatibility"""
        max_words = max_length // 3  # Rough conversion
        return self.summarize_text_with_openai(text, max_words)
    
    def generate_questions(self, text):
        """Tạo câu hỏi gợi ý dựa trên nội dung tài liệu với improved error handling"""
        
        def _get_fallback_questions():
            """Trả về câu hỏi mặc định"""
            return [
                "Nội dung chính của tài liệu là gì?",
                "Các điểm quan trọng được đề cập?",
                "Kết luận chính từ tài liệu này?",
                "Thông tin nào đáng chú ý nhất?"
            ]
        
        # Nếu không có Mistral client, trả về câu hỏi mặc định
        if not self.mistral_client:
            return _get_fallback_questions()
        
        def _call_mistral_questions():
            # Lấy đoạn văn đại diện để tạo câu hỏi
            chunks = self.chunk_text(text, chunk_size=500)
            sample_text = chunks[0] if chunks else text[:500]
            
            prompt = f"""Dựa trên đoạn văn sau, tạo 4 câu hỏi ngắn gọn mà người đọc có thể quan tâm:

{sample_text}

Yêu cầu:
- Mỗi câu hỏi không quá 15 từ
- Tập trung vào thông tin chính
- Phù hợp với nội dung văn bản
- Chỉ trả về 4 câu hỏi, mỗi câu một dòng
"""
            
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Tách câu hỏi thành list
            questions_text = response.choices[0].message.content
            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and '?' in q]
            
            return questions[:4] if questions else []
        
        # Sử dụng safe_execute_with_retry
        success, result, error_message = safe_execute_with_retry(
            _call_mistral_questions,
            max_retries=1,
            delay=0.5,
            context="Mistral Question Generation",
            show_user=False
        )
        
        if success and result and len(result) >= 3:
            return result
        else:
            # Xử lý lỗi cụ thể và trả về câu hỏi phù hợp
            return self._handle_mistral_question_error(error_message, text)
    
    def _handle_mistral_question_error(self, error_message, text):
        """Xử lý lỗi Mistral API khi tạo câu hỏi và tạo câu hỏi thông minh hơn"""
        
        # Lỗi 429 - Rate limit exceeded
        if "429" in str(error_message) or "capacity exceeded" in str(error_message).lower():
            # Tạo câu hỏi thông minh dựa trên nội dung
            return self._generate_smart_questions_from_content(text)
        
        # Lỗi 401/403 - Authentication
        elif "401" in str(error_message) or "403" in str(error_message):
            return [
                "Nội dung chính của tài liệu là gì?",
                "Các thông tin quan trọng được đề cập?",
                "Điểm nổi bật trong tài liệu?",
                "Kết luận chính từ nội dung này?"
            ]
        
        # Lỗi kết nối
        elif "connection" in str(error_message).lower():
            return self._generate_smart_questions_from_content(text)
        
        # Lỗi khác
        else:
            return self._generate_smart_questions_from_content(text)
    
    def _generate_smart_questions_from_content(self, text):
        """Tạo câu hỏi thông minh dựa trên phân tích nội dung"""
        try:
            # Lấy một phần nhỏ của text để phân tích
            sample = text[:800] if len(text) > 800 else text
            sample_lower = sample.lower()
            
            questions = []
            
            # Phân tích keywords để tạo câu hỏi phù hợp
            if any(word in sample_lower for word in ['định nghĩa', 'khái niệm', 'là gì']):
                questions.append("Các khái niệm chính được định nghĩa như thế nào?")
            
            if any(word in sample_lower for word in ['phương pháp', 'cách thức', 'quy trình']):
                questions.append("Phương pháp nào được đề cập trong tài liệu?")
            
            if any(word in sample_lower for word in ['kết quả', 'thành quả', 'hiệu quả']):
                questions.append("Kết quả chính đạt được là gì?")
            
            if any(word in sample_lower for word in ['vấn đề', 'thách thức', 'khó khăn']):
                questions.append("Những vấn đề nào được nêu ra?")
            
            if any(word in sample_lower for word in ['giải pháp', 'đề xuất', 'khuyến nghị']):
                questions.append("Giải pháp nào được đề xuất?")
            
            if any(word in sample_lower for word in ['phân tích', 'nghiên cứu', 'khảo sát']):
                questions.append("Phân tích chính trong tài liệu là gì?")
            
            # Đảm bảo có ít nhất 4 câu hỏi
            default_questions = [
                "Nội dung chính của tài liệu là gì?",
                "Các điểm quan trọng được đề cập?",
                "Thông tin nào đáng chú ý nhất?",
                "Kết luận chính từ tài liệu này?"
            ]
            
            # Kết hợp và loại bỏ trùng lặp
            all_questions = questions + default_questions
            unique_questions = []
            seen = set()
            
            for q in all_questions:
                if q not in seen:
                    unique_questions.append(q)
                    seen.add(q)
                if len(unique_questions) >= 4:
                    break
            
            return unique_questions[:4]
            
        except Exception as e:
            # Fallback cuối cùng
            return [
                "Nội dung chính của tài liệu là gì?",
                "Các điểm quan trọng được đề cập?",
                "Thông tin nào đáng chú ý nhất?",
                "Kết luận chính từ tài liệu này?"
            ]
    
    def answer_question_with_openai(self, question, document_text):
        """Trả lời câu hỏi sử dụng Local LLM với RAG approach"""
        if not document_text:
            return "Không có tài liệu nào để trả lời câu hỏi."
        
        if not self.openai_client:
            return "Không thể kết nối Local LLM. Vui lòng khởi động LM Studio trước."
            
        try:
            # Tìm phần văn bản liên quan đến câu hỏi
            relevant_text = self._find_relevant_text_for_question(question, document_text, max_length=2500)
            
            # Tạo system prompt chuyên biệt cho Q&A
            system_prompt = """Bạn là một AI assistant chuyên trả lời câu hỏi dựa trên tài liệu được cung cấp. 
Hãy trả lời chính xác, chi tiết và dựa hoàn toàn vào nội dung tài liệu. 
Nếu thông tin không có trong tài liệu, hãy nói rõ là không tìm thấy thông tin đó."""
            
            # Tạo user prompt với context và question
            user_prompt = f"""Dựa vào đoạn văn bản sau, hãy trả lời câu hỏi một cách chính xác và chi tiết:

ĐOẠN VĂN BẢN:
{relevant_text}

CÂU HỎI: {question}

Hãy trả lời bằng tiếng Việt, dựa hoàn toàn vào thông tin trong đoạn văn bản trên:"""

            response = self.openai_client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400,
                temperature=0.2,  # Thấp để có câu trả lời chính xác
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Thêm prefix để người dùng biết đây là câu trả lời dựa trên tài liệu
            return f"📄 **Dựa trên tài liệu:** {answer}"
            
        except Exception as e:
            st.error(f"Lỗi khi trả lời câu hỏi với Local LLM: {str(e)}")
            # Fallback với keyword matching
            return self._simple_keyword_answer(question, document_text)
    
    # Để tương thích backward, tạo alias
    def answer_question_with_bart(self, question, document_text):
        """Alias cho backward compatibility"""
        return self.answer_question_with_openai(question, document_text)
    
    def _find_relevant_text_for_question(self, question, document_text, max_length=1500):
        """Tìm phần văn bản liên quan nhất với câu hỏi"""
        # Trích xuất keywords từ câu hỏi
        question_keywords = self._extract_keywords(question.lower())
        
        # Chia document thành các đoạn
        chunks = self.chunk_text(document_text, chunk_size=500, overlap=100)
        
        # Tính điểm relevance cho mỗi chunk
        chunk_scores = []
        for chunk in chunks:
            score = self._calculate_relevance_score(question_keywords, chunk.lower())
            chunk_scores.append((chunk, score))
        
        # Sắp xếp theo điểm số và lấy chunks tốt nhất
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Kết hợp các chunks tốt nhất trong giới hạn max_length
        relevant_text = ""
        current_length = 0
        
        for chunk, score in chunk_scores:
            if score > 0 and current_length + len(chunk) <= max_length:
                relevant_text += chunk + "\n\n"
                current_length += len(chunk)
            if current_length >= max_length:
                break
        
        # Nếu không tìm thấy gì liên quan, lấy phần đầu document
        if not relevant_text.strip():
            relevant_text = document_text[:max_length]
        
        return relevant_text.strip()
    
    def _extract_keywords(self, text):
        """Trích xuất keywords từ text"""
        # Loại bỏ stop words đơn giản
        stop_words = {'là', 'gì', 'của', 'có', 'được', 'này', 'đó', 'và', 'với', 'cho', 'từ', 'trong', 'một', 'các', 'những', 'khi', 'nào', 'ai', 'ở', 'đâu', 'sao', 'như', 'thế', 'what', 'is', 'are', 'the', 'of', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        
        words = text.replace('?', '').replace(',', '').replace('.', '').split()
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords
    
    def _calculate_relevance_score(self, keywords, text):
        """Tính điểm relevance dựa trên số lượng keywords xuất hiện"""
        score = 0
        for keyword in keywords:
            score += text.count(keyword)
        return score
    
    def _simple_keyword_answer(self, question, document_text):
        """Fallback method với keyword matching đơn giản"""
        keywords = self._extract_keywords(question.lower())
        
        # Tìm câu chứa keywords
        sentences = document_text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Lấy tối đa 3 câu liên quan
            result = '. '.join(relevant_sentences[:3])
            return f"Dựa trên tài liệu: {result}."
        else:
            return f"Không tìm thấy thông tin cụ thể về '{question}' trong tài liệu."
    
    def extract_pdf_page_as_image(self, uploaded_file, page_number: int, dpi: int = 150) -> Optional[Image.Image]:
        """
        Convert trang PDF thành hình ảnh PIL Image
        
        Args:
            uploaded_file: File PDF đã upload
            page_number: Số trang cần convert (bắt đầu từ 1)
            dpi: Độ phân giải (mặc định 150 DPI)
            
        Returns:
            PIL Image hoặc None nếu lỗi
        """
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            
            # Mở PDF với PyMuPDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Kiểm tra page number hợp lệ
            if page_number < 1 or page_number > pdf_document.page_count:
                st.error(f"❌ Trang {page_number} không tồn tại. PDF có {pdf_document.page_count} trang.")
                pdf_document.close()
                return None
            
            # Lấy trang (index từ 0)
            page = pdf_document[page_number - 1]
            
            # Tạo matrix với DPI cụ thể
            zoom = dpi / 72.0  # 72 DPI là mặc định
            matrix = fitz.Matrix(zoom, zoom)
            
            # Render trang thành pixmap
            pixmap = page.get_pixmap(matrix=matrix)
            
            # Convert pixmap thành PIL Image
            img_data = pixmap.tobytes("ppm")
            pil_image = Image.open(BytesIO(img_data))
            
            # Đóng resources
            pixmap = None
            pdf_document.close()
            
            return pil_image
            
        except Exception as e:
            st.error(f"❌ Lỗi khi convert PDF sang ảnh: {str(e)}")
            return None
    
    def get_pdf_page_image_base64(self, uploaded_file, page_number: int, dpi: int = 150) -> Optional[str]:
        """
        Convert trang PDF thành base64 string để hiển thị trong Streamlit
        
        Args:
            uploaded_file: File PDF đã upload
            page_number: Số trang cần convert (bắt đầu từ 1)
            dpi: Độ phân giải (mặc định 150 DPI)
            
        Returns:
            Base64 string hoặc None nếu lỗi
        """
        try:
            # Lấy PIL Image
            pil_image = self.extract_pdf_page_as_image(uploaded_file, page_number, dpi)
            
            if pil_image is None:
                return None
            
            # Convert PIL Image thành base64
            buffer = BytesIO()
            pil_image.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return img_base64
            
        except Exception as e:
            st.error(f"❌ Lỗi khi tạo base64 image: {str(e)}")
            return None
    
    def get_pdf_page_count_with_pymupdf(self, uploaded_file) -> int:
        """
        Lấy số trang PDF bằng PyMuPDF (fallback method)
        
        Args:
            uploaded_file: File PDF đã upload
            
        Returns:
            Số trang của PDF
        """
        try:
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            
            # Mở PDF với PyMuPDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = pdf_document.page_count
            pdf_document.close()
            
            return page_count
            
        except Exception as e:
            st.error(f"❌ Lỗi khi đếm trang PDF với PyMuPDF: {str(e)}")
            return 0
    
    def get_pdf_image_dimensions(self, uploaded_file, page_number: int) -> tuple:
        """
        Lấy kích thước gốc của trang PDF
        
        Args:
            uploaded_file: File PDF đã upload
            page_number: Số trang cần kiểm tra
            
        Returns:
            Tuple (width, height) hoặc (0, 0) nếu lỗi
        """
        try:
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            if page_number < 1 or page_number > pdf_document.page_count:
                pdf_document.close()
                return (0, 0)
            
            page = pdf_document[page_number - 1]
            rect = page.rect
            
            pdf_document.close()
            
            return (int(rect.width), int(rect.height))
            
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy kích thước PDF: {str(e)}")
            return (0, 0)
