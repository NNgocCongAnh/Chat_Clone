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
            # Chuẩn bị messages cho OpenAI với enhanced context management
            if is_document_qa and document_context:
                # Specialized system prompt cho document Q&A
                system_content = self._create_document_qa_prompt(document_context)
                max_tokens = 600  # Tăng để có câu trả lời chi tiết hơn
                temperature = 0.15  # Giảm để tăng độ chính xác
            else:
                # Standard chat system prompt với context intelligence
                system_content = self._create_enhanced_system_prompt(document_context, user_input)
                max_tokens = 1200  # Tăng để có phản hồi phong phú hơn
                temperature = 0.6  # Cân bằng giữa creativity và consistency
            
            messages = [
                {
                    "role": "system",
                    "content": system_content
                }
            ]
            
            # Enhanced chat history management với intelligent filtering
            recent_history = self._filter_relevant_history(chat_history, user_input, max_messages=12)
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Thêm tin nhắn hiện tại với context enhancement
            enhanced_input = self._enhance_user_input(user_input, document_context)
            messages.append({
                "role": "user",
                "content": enhanced_input
            })
            
            # Gọi Local LLM API với optimized parameters
            response = self.client.chat.completions.create(
                model="local-model",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,  # Thêm top_p để kiểm soát diversity
                frequency_penalty=0.1,  # Giảm repetition
                presence_penalty=0.1   # Encourage new topics
            )
            
            return response.choices[0].message.content
        
        # Sử dụng safe_execute_with_retry để xử lý lỗi
        success, result, error_message = safe_execute_with_retry(
            _call_llm,
            max_retries=2,  # Tăng lên 2 lần thử
            delay=1.0,      # Tăng delay để model có thời gian
            context="Enhanced Local LLM Chat",
            show_user=False
        )
        
        if success:
            # Post-process response để cải thiện chất lượng
            return self._post_process_response(result, user_input, is_document_qa)
        else:
            # Xử lý các loại lỗi cụ thể với enhanced fallback
            return self._handle_llm_error(error_message, user_input, document_context)
    
    def _create_enhanced_system_prompt(self, document_context, user_input):
        """Tạo system prompt thông minh cho chat với context awareness"""
        base_prompt = """Bạn là Study Buddy - một AI assistant thông minh chuyên hỗ trợ học tập. 

KHẢ NĂNG CỐT LÕI:
- 📚 Phân tích và giải thích tài liệu học tập
- 🤔 Trả lời câu hỏi chi tiết và chính xác  
- 💡 Đưa ra gợi ý học tập thông minh
- 🎯 Tương tác tự nhiên bằng tiếng Việt

NGUYÊN TẮC HOẠT ĐỘNG:
✅ Trả lời chính xác, có căn cứ
✅ Giải thích dễ hiểu, logic rõ ràng
✅ Đưa ra ví dụ cụ thể khi cần
✅ Khuyến khích tư duy phản biện
❌ Không bịa đặt thông tin sai lệch
❌ Không trả lời những câu hỏi không phù hợp"""
        
        if document_context:
            # Intelligent context inclusion dựa trên user input
            context_snippet = self._extract_relevant_context(document_context, user_input)
            base_prompt += f"""

📄 NGỮ CẢNH TÀI LIỆU:
Người dùng đã upload tài liệu. Dưới đây là phần nội dung liên quan:

{context_snippet}

HƯỚNG DẪN SỬ DỤNG TÀI LIỆU:
- Ưu tiên thông tin từ tài liệu khi trả lời
- Trích dẫn cụ thể khi cần thiết
- Ghi rõ nguồn: "Theo tài liệu bạn upload..."
- Kết hợp kiến thức chung khi phù hợp"""
        
        return base_prompt

    def _create_system_prompt(self, document_context):
        """Backward compatibility method"""
        return self._create_enhanced_system_prompt(document_context, "")
    
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

    def _filter_relevant_history(self, chat_history, user_input, max_messages=12):
        """Lọc lịch sử chat có liên quan đến câu hỏi hiện tại"""
        if not chat_history or len(chat_history) <= max_messages:
            return chat_history
        
        # Lấy keywords từ user input
        keywords = user_input.lower().split()
        relevant_messages = []
        
        # Ưu tiên tin nhắn gần đây
        recent_messages = chat_history[-max_messages//2:]
        relevant_messages.extend(recent_messages)
        
        # Tìm tin nhắn có liên quan từ lịch sử cũ hơn
        older_messages = chat_history[:-max_messages//2]
        for msg in reversed(older_messages):
            if len(relevant_messages) >= max_messages:
                break
            
            # Kiểm tra keywords trong nội dung
            msg_content = msg.get("content", "").lower()
            if any(keyword in msg_content for keyword in keywords if len(keyword) > 3):
                relevant_messages.insert(0, msg)
        
        return relevant_messages[-max_messages:]
    
    def _extract_relevant_context(self, document_context, user_input, max_length=2000):
        """Trích xuất phần context liên quan đến câu hỏi"""
        if not document_context or not user_input:
            return document_context[:max_length]
        
        # Tìm keywords trong user input
        keywords = [word.lower() for word in user_input.split() if len(word) > 3]
        
        # Chia document thành chunks
        chunks = []
        chunk_size = 500
        for i in range(0, len(document_context), chunk_size):
            chunk = document_context[i:i+chunk_size]
            chunks.append(chunk)
        
        # Tính score cho mỗi chunk
        chunk_scores = []
        for chunk in chunks:
            score = 0
            chunk_lower = chunk.lower()
            for keyword in keywords:
                score += chunk_lower.count(keyword)
            chunk_scores.append((chunk, score))
        
        # Sắp xếp và lấy chunks có score cao
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        
        relevant_text = ""
        current_length = 0
        
        for chunk, score in chunk_scores:
            if current_length + len(chunk) <= max_length:
                relevant_text += chunk + "\n"
                current_length += len(chunk)
            else:
                break
        
        return relevant_text.strip() or document_context[:max_length]
    
    def _enhance_user_input(self, user_input, document_context):
        """Cải thiện user input với context hints"""
        if not document_context:
            return user_input
        
        # Thêm context hint nếu user input quá ngắn
        if len(user_input.split()) <= 3:
            return f"{user_input}\n\n(Gợi ý: Tham khảo tài liệu đã upload để trả lời chi tiết hơn)"
        
        return user_input
    
    def _post_process_response(self, response, user_input, is_document_qa):
        """Xử lý và cải thiện phản hồi từ LLM"""
        if not response:
            return "Xin lỗi, tôi không thể tạo phản hồi phù hợp. Bạn có thể thử lại với câu hỏi khác không?"
        
        # Loại bỏ các ký tự không mong muốn
        response = response.strip()
        
        # Thêm emoji và formatting cho document Q&A
        if is_document_qa and not response.startswith(("📄", "🤖", "✅", "❌", "⚠️")):
            response = f"📄 **Dựa trên tài liệu:** {response}"
        
        # Đảm bảo phản hồi không quá dài
        if len(response) > 2000:
            response = response[:1900] + "\n\n...(Phản hồi đã được rút gọn)"
        
        return response
