import streamlit as st
import openai
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatHandler:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            try:
                self.api_key = st.secrets.get("OPENAI_API_KEY", "")
            except Exception:
                self.api_key = ""
        
        if self.api_key:
            openai.api_key = self.api_key
        else:
            st.warning("⚠️ Chưa cấu hình OpenAI API Key. Ứng dụng sẽ chạy ở chế độ demo.")
    
    def generate_response(self, user_input, chat_history, document_context=""):
        """Tạo phản hồi từ AI"""
        
        # Nếu không có API key, trả về phản hồi demo
        if not self.api_key:
            return self._generate_demo_response(user_input, document_context)
        
        try:
            # Chuẩn bị messages cho OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self._create_system_prompt(document_context)
                }
            ]
            
            # Thêm lịch sử chat (giới hạn 10 tin nhắn gần nhất)
            recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Thêm tin nhắn hiện tại
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Gọi OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Lỗi khi gọi OpenAI API: {str(e)}")
            return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."
    
    def _create_system_prompt(self, document_context):
        """Tạo system prompt"""
        base_prompt = """Bạn là một AI assistant thông minh và hữu ích. Hãy trả lời các câu hỏi một cách chi tiết và chính xác. Sử dụng tiếng Việt để trả lời."""
        
        if document_context:
            base_prompt += f"""
            
THÔNG TIN TÀI LIỆU:
Người dùng đã upload các tài liệu sau. Hãy sử dụng thông tin này để trả lời câu hỏi khi phù hợp:

{document_context[:3000]}...

Khi trả lời dựa trên tài liệu, hãy ghi rõ bạn đang tham khảo từ tài liệu đã upload.
"""
        
        return base_prompt
    
    def _generate_demo_response(self, user_input, document_context):
        """Tạo phản hồi demo khi không có API key"""
        if document_context:
            return f"""🤖 **Phản hồi Demo với Tài liệu**

Câu hỏi của bạn: "{user_input}"

Dựa trên tài liệu bạn đã upload, tôi có thể thấy:
- Tài liệu chứa {len(document_context)} ký tự
- Nội dung liên quan đến câu hỏi của bạn

**Lưu ý:** Đây là chế độ demo. Để có trải nghiệm đầy đủ, vui lòng cấu hình OpenAI API Key trong file `.env` hoặc Streamlit secrets.

**Cách cấu hình:**
1. Tạo file `.env` trong thư mục gốc
2. Thêm dòng: `OPENAI_API_KEY=your-api-key-here`
3. Hoặc thêm vào Streamlit secrets: `OPENAI_API_KEY = "your-api-key-here"`

Preview nội dung tài liệu: {document_context[:200]}..."""
        
        return f"""🤖 **Phản hồi Demo**

Câu hỏi của bạn: "{user_input}"

Xin chào! Tôi là ChatGPT Clone được xây dựng bằng Streamlit. Hiện tại đang chạy ở chế độ demo.

**Tính năng có sẵn:**
- ✅ Giao diện chat giống ChatGPT
- ✅ Upload và xử lý tài liệu (PDF, DOCX, TXT, MD)
- ✅ Lưu lịch sử chat
- ✅ Sidebar quản lý tài liệu

**Để kích hoạt AI thật:**
1. Tạo file `.env` với: `OPENAI_API_KEY=your-key`
2. Hoặc cấu hình trong Streamlit secrets

Thời gian: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"""
