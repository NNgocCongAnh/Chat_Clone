import streamlit as st
import openai
from datetime import datetime
import os
from dotenv import load_dotenv
from .error_handler import handle_error, LLMConnectionError, safe_execute_with_retry

# Load environment variables
load_dotenv()

class ChatHandler:
    def __init__(self):
        # Khởi tạo Local LLM client (LM Studio)
        self.local_llm_url = os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1")
        try:
            self.client = openai.OpenAI(
                base_url=self.local_llm_url,
                api_key="not_needed"
            )
            self.api_key = "local_connected"  # Để tương thích với logic cũ
            st.success("✅ ChatHandler đã kết nối Local LLM (LM Studio)")
        except Exception as e:
            self.client = None
            self.api_key = None
            st.warning(f"⚠️ ChatHandler không thể kết nối Local LLM: {str(e)}. Ứng dụng sẽ chạy ở chế độ demo.")
    
    def generate_response(self, user_input, chat_history, document_context="", is_document_qa=False):
        """Tạo phản hồi từ AI với enhanced document Q&A support và improved error handling"""
        
        # Nếu không có API key, trả về phản hồi demo
        if not self.api_key:
            return self._generate_demo_response(user_input, document_context)
        
        def _call_llm():
            # Chuẩn bị messages cho OpenAI
            if is_document_qa and document_context:
                # Specialized system prompt cho document Q&A
                system_content = self._create_document_qa_prompt(document_context)
                max_tokens = 500  # Focused answers
                temperature = 0.2  # More deterministic
            else:
                # Standard chat system prompt
                system_content = self._create_system_prompt(document_context)
                max_tokens = 1000
                temperature = 0.7
            
            messages = [
                {
                    "role": "system",
                    "content": system_content
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
            
            # Gọi Local LLM API
            response = self.client.chat.completions.create(
                model="local-model",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content
        
        # Sử dụng safe_execute_with_retry để xử lý lỗi
        success, result, error_message = safe_execute_with_retry(
            _call_llm,
            max_retries=1,  # Chỉ thử 1 lần vì Local LLM
            delay=0.5,
            context="Local LLM Chat",
            show_user=False  # Không hiển thị lỗi raw
        )
        
        if success:
            return result
        else:
            # Xử lý các loại lỗi cụ thể
            return self._handle_llm_error(error_message, user_input, document_context)
    
    def _create_system_prompt(self, document_context):
        """Tạo system prompt cho chat thông thường"""
        base_prompt = """Bạn là một AI assistant thông minh và hữu ích. Hãy trả lời các câu hỏi một cách chi tiết và chính xác. Sử dụng tiếng Việt để trả lời."""
        
        if document_context:
            base_prompt += f"""
            
THÔNG TIN TÀI LIỆU:
Người dùng đã upload các tài liệu sau. Hãy sử dụng thông tin này để trả lời câu hỏi khi phù hợp:

{document_context[:3000]}...

Khi trả lời dựa trên tài liệu, hãy ghi rõ bạn đang tham khảo từ tài liệu đã upload.
"""
        
        return base_prompt
    
    def _create_document_qa_prompt(self, document_context):
        """Tạo system prompt chuyên biệt cho document Q&A"""
        return f"""Bạn là một AI assistant chuyên trả lời câu hỏi dựa trên tài liệu được cung cấp.

NHIỆM VỤ:
- Trả lời câu hỏi chính xác và chi tiết dựa trên nội dung tài liệu
- Chỉ sử dụng thông tin có trong tài liệu
- Nếu không tìm thấy thông tin, hãy nói rõ
- Trả lời bằng tiếng Việt, súc tích và dễ hiểu

NGUYÊN TẮC:
✅ Dựa hoàn toàn vào nội dung tài liệu
✅ Trích dẫn cụ thể khi cần thiết  
✅ Thừa nhận khi không có thông tin
❌ Không bịa đặt thông tin không có trong tài liệu
❌ Không suy diễn quá xa

TÀI LIỆU THAM KHẢO:
{document_context[:2500]}

Hãy trả lời câu hỏi dựa trên tài liệu trên."""
    
    def _generate_demo_response(self, user_input, document_context):
        """Tạo phản hồi demo khi không có Local LLM connection"""
        if document_context:
            return f"""🤖 **Phản hồi Demo với Tài liệu**

Câu hỏi của bạn: "{user_input}"

Dựa trên tài liệu bạn đã upload, tôi có thể thấy:
- Tài liệu chứa {len(document_context)} ký tự
- Nội dung liên quan đến câu hỏi của bạn

**Lưu ý:** Đây là chế độ demo. Để có trải nghiệm đầy đủ với Local LLM:

**Cách kích hoạt:**
1. 🚀 Khởi động LM Studio trên port 1234
2. 📁 Load một model bất kỳ (llama, mistral, etc.)
3. ▶️ Restart ứng dụng Streamlit

Preview nội dung tài liệu: {document_context[:200]}..."""
        
        return f"""🤖 **Phản hồi Demo - Local LLM**

Câu hỏi của bạn: "{user_input}"

Xin chào! Tôi là Study Buddy với Local LLM support. Hiện tại đang chạy ở chế độ demo.

**🎯 Để demo hoạt động đầy đủ:**

**Bước 1:** Khởi động LM Studio
- Download LM Studio từ: https://lmstudio.ai
- Mở LM Studio và start server trên port 1234

**Bước 2:** Load Model
- Download một model (llama, mistral, phi, v.v.)
- Load model và start local server

**Bước 3:** Restart App
- Restart ứng dụng Streamlit này
- Bạn sẽ thấy "✅ Đã kết nối Local LLM"

**💡 Lợi ích Local LLM:**
- ✅ Hoàn toàn miễn phí
- ✅ Chạy offline 
- ✅ Privacy tuyệt đối
- ✅ Demo ổn định

Thời gian: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"""
    
    def _handle_llm_error(self, error_message, user_input, document_context):
        """Xử lý các loại lỗi LLM cụ thể và trả về phản hồi thân thiện"""
        
        # Xử lý lỗi 404 - No models loaded
        if "404" in str(error_message) and "model_not_found" in str(error_message):
            return f"""⚠️ **Local LLM chưa sẵn sàng**

Câu hỏi của bạn: "{user_input}"

**🔧 Nguyên nhân:** LM Studio chưa load model nào.

**💡 Cách khắc phục:**
1. 🚀 Mở LM Studio
2. 📁 Tải và load một model (ví dụ: Llama, Mistral, Phi)
3. ▶️ Start local server trên port 1234
4. 🔄 Refresh lại trang này

**📋 Hướng dẫn chi tiết:**
- Download LM Studio: https://lmstudio.ai
- Chọn tab "Chat" → Load model → Start server
- Đảm bảo server chạy trên `http://localhost:1234`

**🎯 Trạng thái hiện tại:** Chế độ chờ Local LLM
⏰ {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"""

        # Xử lý lỗi connection
        elif "connection" in str(error_message).lower() or "connect" in str(error_message).lower():
            return f"""🔌 **Lỗi kết nối Local LLM**

Câu hỏi của bạn: "{user_input}"

**🔧 Nguyên nhân:** Không thể kết nối đến LM Studio server.

**💡 Cách khắc phục:**
1. ✅ Kiểm tra LM Studio đã chạy chưa
2. 🌐 Đảm bảo server trên port 1234
3. 🔒 Tắt firewall/antivirus tạm thời
4. 🔄 Restart LM Studio và ứng dụng này

**📊 Thông tin kỹ thuật:**
- URL: {self.local_llm_url}
- Trạng thái: Mất kết nối

⏰ {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"""

        # Xử lý lỗi timeout
        elif "timeout" in str(error_message).lower():
            return f"""⏱️ **Local LLM phản hồi chậm**

Câu hỏi của bạn: "{user_input}"

**🔧 Nguyên nhân:** Model xử lý quá lâu hoặc server quá tải.

**💡 Gợi ý:**
1. 🔄 Thử lại với câu hỏi ngắn hơn
2. ⚡ Chọn model nhỏ hơn trong LM Studio
3. 🖥️ Đóng các ứng dụng khác để giải phóng RAM
4. ⏰ Chờ một chút rồi thử lại

**📊 Model hiện tại có thể quá lớn cho máy này**

⏰ {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"""
        
        # Lỗi general fallback
        else:
            return f"""🤖 **Tạm thời không thể phản hồi**

Câu hỏi của bạn: "{user_input}"

**🔧 Đang gặp sự cố kỹ thuật với Local LLM**

**💡 Có thể thử:**
1. 🔄 Thử lại sau vài giây
2. 🚀 Restart LM Studio
3. 📱 Kiểm tra model đã load đúng chưa
4. 💻 Restart ứng dụng này

**🎯 Chế độ dự phòng:** Demo mode
- Ứng dụng vẫn hoạt động bình thường
- Local LLM sẽ tự phục hồi khi sẵn sàng

⏰ {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}
🔧 Lỗi: {str(error_message)[:100]}..."""
