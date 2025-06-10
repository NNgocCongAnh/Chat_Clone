import streamlit as st
from datetime import datetime

def render_message(message):
    """Render một tin nhắn chat với style giống ChatGPT"""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", datetime.now())
    
    if role == "user":
        # Tin nhắn của user - căn phải
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
            st.caption(f"🕐 {timestamp.strftime('%H:%M')}")
    
    elif role == "assistant":
        # Tin nhắn của AI - căn trái
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)
            st.caption(f"🕐 {timestamp.strftime('%H:%M')}")

def render_sidebar():
    """Render sidebar với thông tin và điều khiển"""
    with st.sidebar:
        st.markdown("### 💬 ChatGPT Clone")
        st.markdown("---")
        
        # Thông tin ứng dụng
        st.markdown("""
        **Tính năng:**
        - 💬 Chat với AI
        - 📄 Upload tài liệu
        - 🔍 Tìm kiếm trong tài liệu
        - 💾 Lưu lịch sử chat
        """)
        
        st.markdown("---")
        
        # Hướng dẫn sử dụng
        with st.expander("📖 Hướng dẫn sử dụng"):
            st.markdown("""
            **Cách sử dụng:**
            1. Upload tài liệu (PDF, DOCX, TXT, MD)
            2. Đặt câu hỏi hoặc chat bình thường
            3. AI sẽ trả lời dựa trên nội dung tài liệu
            4. Sử dụng nút "Xóa lịch sử" để reset chat
            
            **Mẹo:**
            - Hỏi cụ thể về nội dung tài liệu
            - Yêu cầu tóm tắt, phân tích
            - Chat đa dạng chủ đề
            """)
        
        # Thông tin phiên bản
        st.markdown("---")
        st.markdown("**Phiên bản:** 1.0.0")
        st.markdown("**Công nghệ:** Streamlit + OpenAI")

def render_document_preview(doc_content, max_chars=500):
    """Hiển thị preview nội dung tài liệu"""
    if len(doc_content) > max_chars:
        preview = doc_content[:max_chars] + "..."
    else:
        preview = doc_content
    
    st.text_area(
        "Preview nội dung:",
        value=preview,
        height=200,
        disabled=True
    )

def render_chat_stats(messages):
    """Hiển thị thống kê chat"""
    if not messages:
        return
    
    user_msgs = len([m for m in messages if m["role"] == "user"])
    ai_msgs = len([m for m in messages if m["role"] == "assistant"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tin nhắn của bạn", user_msgs)
    with col2:
        st.metric("Phản hồi AI", ai_msgs)

def create_download_link(messages):
    """Tạo link download lịch sử chat"""
    if not messages:
        return None
    
    # Tạo nội dung file
    content = f"# Lịch sử Chat - {datetime.now().strftime('%Y%m%d_%H%M%S')}\n\n"
    
    for i, msg in enumerate(messages, 1):
        role = "👤 Bạn" if msg["role"] == "user" else "🤖 AI"
        timestamp = msg.get("timestamp", datetime.now()).strftime('%H:%M %d/%m/%Y')
        content += f"## {i}. {role} ({timestamp})\n\n{msg['content']}\n\n---\n\n"
    
    return content

def show_upload_tips():
    """Hiển thị tips cho việc upload tài liệu"""
    st.info("""
    💡 **Mẹo upload tài liệu:**
    - **PDF:** Hỗ trợ text PDF (không phải ảnh scan)
    - **DOCX:** File Word định dạng .docx
    - **TXT/MD:** File text thuần với encoding UTF-8
    - **Kích thước:** Tối đa 200MB mỗi file
    """)

def render_error_message(error_msg):
    """Hiển thị thông báo lỗi với format đẹp"""
    st.error(f"❌ **Lỗi:** {error_msg}")

def render_success_message(success_msg):
    """Hiển thị thông báo thành công"""
    st.success(f"✅ **Thành công:** {success_msg}")

def render_warning_message(warning_msg):
    """Hiển thị thông báo cảnh báo"""
    st.warning(f"⚠️ **Cảnh báo:** {warning_msg}")

def create_message_container():
    """Tạo container cho messages với style tùy chỉnh"""
    return st.container()

def add_custom_css():
    """Thêm CSS tùy chỉnh cho giao diện"""
    st.markdown("""
    <style>
    /* Custom styles cho chat interface */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        margin-left: 20%;
    }
    
    .assistant-message {
        background-color: #f1f3f4;
        color: #333;
        margin-right: 20%;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #0056b3, #004085);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
