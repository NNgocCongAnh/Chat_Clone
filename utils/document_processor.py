import docx
import streamlit as st
from io import BytesIO
import base64
from mistralai import Mistral
import os
import time
from transformers import pipeline

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
        
        # Khởi tạo BART summarization pipeline
        self.summarizer = None
        self.embeddings_cache = {}
    
    def process_document(self, uploaded_file):
        """Xử lý và trích xuất text từ tài liệu đã upload"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                return self.extract_pdf_content(uploaded_file)
            elif file_extension == 'docx':
                return self.extract_docx_content(uploaded_file)
            elif file_extension in ['txt', 'md']:
                return self.extract_text_content(uploaded_file)
            else:
                st.error(f"Định dạng file {file_extension} không được hỗ trợ")
                return None
                
        except Exception as e:
            st.error(f"Lỗi khi xử lý tài liệu: {str(e)}")
            return None
    
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
                
                # Trích xuất nội dung từ tất cả các trang
                content = ""
                for page in ocr_response.pages:
                    if hasattr(page, 'markdown') and page.markdown:
                        content += page.markdown + "\n\n"
                
                return content.strip() if content else None
                
        except Exception as e:
            st.error(f"Lỗi khi xử lý PDF với Mistral OCR: {str(e)}")
            return None
    
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
    
    def initialize_summarizer(self):
        """Khởi tạo BART summarizer (lazy loading)"""
        if self.summarizer is None:
            try:
                with st.spinner("Đang tải BART model để tóm tắt..."):
                    self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
                st.success("✅ BART model đã sẵn sàng!")
            except Exception as e:
                st.error(f"Không thể tải BART model: {str(e)}")
                return False
        return True
    
    def summarize_text(self, text, max_length=200, min_length=50):
        """Tóm tắt văn bản sử dụng BART"""
        if not self.initialize_summarizer():
            return None
            
        try:
            # Chia text thành chunks nhỏ hơn nếu quá dài
            max_input_length = 1024
            if len(text) > max_input_length:
                chunks = self.chunk_text(text, chunk_size=max_input_length, overlap=100)
                summaries = []
                
                for chunk in chunks[:3]:  # Giới hạn 3 chunks để tránh quá tải
                    if len(chunk.strip()) > 100:  # Chỉ tóm tắt chunk có ý nghĩa
                        summary = self.summarizer(
                            chunk, 
                            max_length=max_length//len(chunks), 
                            min_length=min_length//len(chunks), 
                            do_sample=False
                        )
                        summaries.append(summary[0]['summary_text'])
                
                # Kết hợp các tóm tắt
                combined_summary = " ".join(summaries)
                
                # Tóm tắt lần cuối nếu vẫn quá dài
                if len(combined_summary) > max_length:
                    final_summary = self.summarizer(
                        combined_summary, 
                        max_length=max_length, 
                        min_length=min_length, 
                        do_sample=False
                    )
                    return final_summary[0]['summary_text']
                else:
                    return combined_summary
            else:
                summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
                return summary[0]['summary_text']
                
        except Exception as e:
            st.error(f"Lỗi khi tóm tắt: {str(e)}")
            return None
    
    def generate_questions(self, text):
        """Tạo câu hỏi gợi ý dựa trên nội dung tài liệu"""
        if not self.mistral_client:
            # Fallback questions nếu không có Mistral API
            return [
                "Nội dung chính của tài liệu là gì?",
                "Các điểm quan trọng được đề cập?",
                "Kết luận chính từ tài liệu này?"
            ]
        
        try:
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
            
            # Đảm bảo có ít nhất 3 câu hỏi
            if len(questions) < 3:
                questions.extend([
                    "Thông tin chính trong tài liệu?",
                    "Các điểm quan trọng được nhấn mạnh?",
                    "Kết luận từ nội dung này?"
                ])
            
            return questions[:4]  # Giới hạn 4 câu hỏi
            
        except Exception as e:
            st.error(f"Lỗi khi tạo câu hỏi: {str(e)}")
            return [
                "Nội dung chính của tài liệu là gì?",
                "Các điểm quan trọng được đề cập?",
                "Kết luận chính từ tài liệu này?"
            ]
    
    def answer_question_with_bart(self, question, document_text):
        """Trả lời câu hỏi sử dụng BART với question-focused summarization"""
        if not document_text:
            return "Không có tài liệu nào để trả lời câu hỏi."
        
        try:
            if not self.initialize_summarizer():
                return "Không thể khởi tạo BART model để trả lời."
            
            # Tìm phần văn bản liên quan đến câu hỏi
            relevant_text = self._find_relevant_text_for_question(question, document_text)
            
            # Tạo prompt tập trung vào câu hỏi cho BART
            focused_prompt = f"""Please summarize the following text to answer this specific question: "{question}"

Text to analyze:
{relevant_text}

Focus only on information that directly answers the question. If the answer is not in the text, say so."""
            
            # BART summarize với focus vào câu hỏi
            answer = self.summarizer(
                focused_prompt,
                max_length=200,
                min_length=40,
                do_sample=False,
                num_beams=4
            )
            
            return answer[0]['summary_text']
            
        except Exception as e:
            st.error(f"Lỗi khi trả lời câu hỏi với BART: {str(e)}")
            # Fallback với thông tin cụ thể hơn
            return self._simple_keyword_answer(question, document_text)
    
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
