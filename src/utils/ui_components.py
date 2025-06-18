import streamlit as st
from datetime import datetime
import time

# Enhanced UI Components for Study Buddy
# Author: Nguyễn Ngọc Công Anh - Frontend & UI/UX Enhancement

def render_message(message):
    """Enhanced message rendering với typing animation và status indicators"""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", datetime.now())
    
    if role == "user":
        # Enhanced user message với gradient background
        with st.chat_message("user", avatar="👤"):
            # Message với enhanced formatting
            st.markdown(f"""
            <div class="user-message-content">
                {content}
                <div class="message-metadata">
                    <span class="timestamp">🕐 {timestamp.strftime('%H:%M')}</span>
                    <span class="status-indicator">✓</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif role == "assistant":
        # Enhanced AI message với typing animation
        with st.chat_message("assistant", avatar="🤖"):
            # Simulate typing animation cho messages mới
            if message.get("is_new", False):
                render_typing_animation()
                time.sleep(0.5)  # Brief pause for effect
            
            # Process content để render markdown
            # Loại bỏ emoji và format đặc biệt, chỉ giữ nội dung markdown
            processed_content = content
            
            # Xử lý format "📄 **Dựa trên tài liệu:**" thành markdown heading
            if processed_content.startswith("📄 **Dựa trên tài liệu:**"):
                processed_content = processed_content.replace("📄 **Dựa trên tài liệu:**", "### 📄 Dựa trên tài liệu:\n")
            
            # Render content dưới dạng markdown
            st.markdown(processed_content, unsafe_allow_html=False)
            
            # Metadata với styling
            st.markdown(f"""
            <div class="message-metadata">
                <span class="timestamp">🕐 {timestamp.strftime('%H:%M')}</span>
                <span class="ai-indicator">🤖 Study Buddy</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Message actions
            render_message_actions(content)

def render_typing_animation():
    """Render typing indicator animation"""
    typing_placeholder = st.empty()
    
    # Animated typing dots
    for i in range(3):
        dots = "." * (i + 1)
        typing_placeholder.markdown(f"""
        <div class="typing-indicator">
            <span>🤖 Study Buddy đang soạn tin nhắn{dots}</span>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.3)
    
    typing_placeholder.empty()

def render_message_actions(content):
    """Render action buttons cho messages"""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
    
    with col1:
        if st.button("👍", key=f"like_{hash(content)}", help="Thích tin nhắn này"):
            st.success("👍 Đã thích!")
    
    with col2:
        if st.button("📋", key=f"copy_{hash(content)}", help="Copy tin nhắn"):
            # JavaScript copy functionality would go here
            st.info("📋 Đã copy!")
    
    with col3:
        if st.button("🔄", key=f"regenerate_{hash(content)}", help="Tạo lại phản hồi"):
            st.info("🔄 Tính năng tạo lại đang được phát triển...")

def render_sidebar():
    """Render sidebar với thông tin và điều khiển"""
    with st.sidebar:
        st.markdown("### 💬 Study Buddy")
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

def render_question_carousel(questions, document_text):
    """Render carousel câu hỏi gợi ý với nút điều hướng trái phải"""
    if not questions:
        return
    
    # Khởi tạo session state cho carousel
    if "carousel_start_index" not in st.session_state:
        st.session_state.carousel_start_index = 0
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    if "question_processed" not in st.session_state:
        st.session_state.question_processed = False
    
    # Xử lý pending question trước khi render
    if st.session_state.pending_question and not st.session_state.question_processed:
        st.session_state.question_processed = True
        question = st.session_state.pending_question
        
        # Kiểm tra nếu user đã login
        if not (hasattr(st.session_state, 'user_id') and st.session_state.user_id):
            st.error("❌ Vui lòng đăng nhập để sử dụng chat!")
            st.session_state.pending_question = None
            st.session_state.question_processed = False
            return
        
        # Tạo session mới nếu chưa có
        if not st.session_state.current_session_id:
            smart_title = st.session_state.chat_persistence.generate_smart_title(question)
            session_id = st.session_state.chat_persistence.create_session(
                st.session_state.user_id, 
                smart_title
            )
            
            if session_id:
                st.session_state.current_session_id = session_id
                # Refresh sessions list
                st.session_state.user_sessions = st.session_state.chat_persistence.get_user_sessions(st.session_state.user_id)
        
        # Thêm user message
        st.session_state.messages.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now()
        })
        
        # Lưu user message vào database
        if st.session_state.current_session_id:
            st.session_state.chat_persistence.save_message(
                st.session_state.user_id,
                st.session_state.current_session_id,
                "user",
                question
            )
        
        # Tạo response
        if document_text and hasattr(st.session_state, 'doc_processor'):
            with st.spinner("🤖 Đang trả lời..."):
                response = st.session_state.doc_processor.answer_question_with_openai(
                    question,
                    document_text
                )
        else:
            response = "Vui lòng upload tài liệu để tôi có thể trả lời câu hỏi này."
        
        # Thêm AI response
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now()
        })
        
        # Lưu AI response vào database
        if st.session_state.current_session_id:
            st.session_state.chat_persistence.save_message(
                st.session_state.user_id,
                st.session_state.current_session_id,
                "assistant",
                response
            )
        
        # Reset pending question
        st.session_state.pending_question = None
        st.session_state.question_processed = False
        st.rerun()
    
    # Số câu hỏi hiển thị cùng lúc (responsive)
    questions_per_view = 3
    total_questions = len(questions)
    max_start_index = max(0, total_questions - questions_per_view)
    
    # Container cho carousel
    st.markdown("""
    <div class="questions-carousel-container">
        <h4 style="margin-bottom: 1rem; color: #374151; font-size: 1.1rem;">
            💡 Câu hỏi gợi ý
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Tạo layout với nút trái, câu hỏi, nút phải
    col_left, col_questions, col_right = st.columns([0.8, 8.4, 0.8])
    
    # Nút điều hướng trái
    with col_left:
        if st.button("◀", key="carousel_left", disabled=(st.session_state.carousel_start_index <= 0)):
            st.session_state.carousel_start_index = max(0, st.session_state.carousel_start_index - 1)
            st.rerun()
    
    # Hiển thị câu hỏi
    with col_questions:
        # Lấy câu hỏi hiện tại để hiển thị
        end_index = min(st.session_state.carousel_start_index + questions_per_view, total_questions)
        current_questions = questions[st.session_state.carousel_start_index:end_index]
        
        # Tạo columns cho các câu hỏi
        if len(current_questions) == 1:
            cols = st.columns(1)
        elif len(current_questions) == 2:
            cols = st.columns(2)
        else:
            cols = st.columns(3)
        
        # Check if processing
        processing = st.session_state.pending_question is not None
        
        # Hiển thị từng câu hỏi
        for i, question in enumerate(current_questions):
            with cols[i]:
                question_index = st.session_state.carousel_start_index + i
                # Unique key với hash để tránh collision
                button_key = f"q_{hash(question)}_{question_index}"
                
                if st.button(
                    f"💭 {question}", 
                    key=button_key,
                    use_container_width=True,
                    help=f"Nhấn để hỏi: {question}",
                    disabled=processing  # Disable khi đang xử lý
                ):
                    # Set pending question thay vì xử lý ngay
                    st.session_state.pending_question = question
                    st.rerun()
    
    # Nút điều hướng phải
    with col_right:
        if st.button("▶", key="carousel_right", disabled=(st.session_state.carousel_start_index >= max_start_index)):
            st.session_state.carousel_start_index = min(max_start_index, st.session_state.carousel_start_index + 1)
            st.rerun()
    
    # Hiển thị indicator dots
    if total_questions > questions_per_view:
        total_pages = (total_questions - 1) // questions_per_view + 1
        current_page = st.session_state.carousel_start_index // questions_per_view
        
        dots_html = '<div class="carousel-indicators">'
        for page in range(total_pages):
            if page == current_page:
                dots_html += '<span class="dot active">●</span>'
            else:
                dots_html += '<span class="dot">○</span>'
        dots_html += '</div>'
        
        st.markdown(dots_html, unsafe_allow_html=True)

def add_custom_css():
    """Enhanced CSS với modern animations và glassmorphism effects"""
    st.markdown("""
    <style>
    /* Enhanced Custom styles cho modern chat interface */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --shadow-light: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --blur-strength: blur(8px);
    }
    
    /* Glassmorphism chat message containers */
    .user-message-content {
        background: var(--glass-bg);
        backdrop-filter: var(--blur-strength);
        -webkit-backdrop-filter: var(--blur-strength);
        border-radius: 20px;
        border: 1px solid var(--glass-border);
        padding: 1.2rem;
        box-shadow: var(--shadow-light);
        position: relative;
        overflow: hidden;
    }
    
    .user-message-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--primary-gradient);
        opacity: 0.8;
        z-index: -1;
    }
    
    .assistant-message-content {
        background: rgba(248, 250, 252, 0.9);
        backdrop-filter: var(--blur-strength);
        -webkit-backdrop-filter: var(--blur-strength);
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 1.2rem;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1);
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .assistant-message-content:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px 0 rgba(0, 0, 0, 0.15);
    }
    
    /* Enhanced message metadata */
    .message-metadata {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    .timestamp {
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
    }
    
    .status-indicator {
        background: rgba(34, 197, 94, 0.9);
        color: white;
        padding: 2px 6px;
        border-radius: 50%;
        font-size: 0.7rem;
        font-weight: bold;
    }
    
    .ai-indicator {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced typing animation */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: rgba(248, 250, 252, 0.95);
        border-radius: 20px;
        margin: 0.5rem 0;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    .typing-indicator span {
        color: #6366f1;
        font-weight: 500;
        animation: typing-text 1.5s ease-in-out infinite;
    }
    
    @keyframes typing-text {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* Enhanced button styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px 0 rgba(102, 126, 234, 0.6);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Message action buttons */
    .stButton[key*="like_"] > button {
        background: linear-gradient(135deg, #ec4899, #be185d);
        padding: 0.4rem 0.8rem;
        font-size: 0.8rem;
        min-width: auto;
        box-shadow: 0 2px 8px 0 rgba(236, 72, 153, 0.3);
    }
    
    .stButton[key*="copy_"] > button {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        box-shadow: 0 2px 8px 0 rgba(6, 182, 212, 0.3);
    }
    
    .stButton[key*="regenerate_"] > button {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        box-shadow: 0 2px 8px 0 rgba(245, 158, 11, 0.3);
    }
    
    /* Enhanced sidebar styling với glassmorphism */
    .sidebar .sidebar-content {
        background: linear-gradient(145deg, rgba(248, 250, 252, 0.9), rgba(241, 245, 249, 0.9));
        backdrop-filter: var(--blur-strength);
        -webkit-backdrop-filter: var(--blur-strength);
        border-right: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    /* Enhanced file uploader với modern animations */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, rgba(248, 250, 252, 0.9), rgba(255, 255, 255, 0.9));
        backdrop-filter: var(--blur-strength);
        -webkit-backdrop-filter: var(--blur-strength);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .uploadedFile::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s;
        opacity: 0;
    }
    
    .uploadedFile:hover {
        border-color: #764ba2;
        transform: translateY(-5px);
        box-shadow: 0 15px 35px 0 rgba(102, 126, 234, 0.3);
    }
    
    .uploadedFile:hover::before {
        opacity: 1;
        top: -25%;
        left: -25%;
    }
    
    /* Loading states với modern spinners */
    .stSpinner {
        border-color: #667eea !important;
    }
    
    /* Custom loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid rgba(102, 126, 234, 0.3);
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
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
    
    /* Question Carousel Styles */
    .questions-carousel-container {
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #f8f9ff, #ffffff);
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Carousel navigation buttons */
    .stButton[data-testid*="carousel_left"] > button,
    .stButton[data-testid*="carousel_right"] > button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        padding: 0;
        font-size: 1.2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        border: none;
        color: white;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton[data-testid*="carousel_left"] > button:hover,
    .stButton[data-testid*="carousel_right"] > button:hover {
        background: linear-gradient(135deg, #4f46e5, #4338ca);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    
    .stButton[data-testid*="carousel_left"] > button:disabled,
    .stButton[data-testid*="carousel_right"] > button:disabled {
        background: #d1d5db;
        color: #9ca3af;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Question buttons in carousel */
    .stButton[data-testid*="carousel_question"] > button {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        color: #1f2937;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        line-height: 1.4;
        height: auto;
        min-height: 60px;
        transition: all 0.3s ease;
        text-align: left;
        word-wrap: break-word;
        white-space: normal;
    }
    
    .stButton[data-testid*="carousel_question"] > button:hover {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        border-color: #007bff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
    }
    
    /* Carousel indicators */
    .carousel-indicators {
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .carousel-indicators .dot {
        margin: 0 4px;
        font-size: 1.2rem;
        color: #d1d5db;
        transition: color 0.3s ease;
    }
    
    .carousel-indicators .dot.active {
        color: #007bff;
    }
    
    /* Responsive design cho carousel */
    @media (max-width: 768px) {
        .questions-carousel-container {
            margin: 0.5rem 0;
            padding: 0.75rem;
        }
        
        .stButton[data-testid*="carousel_question"] > button {
            font-size: 0.8rem;
            min-height: 50px;
            padding: 0.5rem 0.75rem;
        }
        
        .stButton[data-testid*="carousel_left"] > button,
        .stButton[data-testid*="carousel_right"] > button {
            width: 35px;
            height: 35px;
            font-size: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_page_selector(documents, doc_processor):
    """Render giao diện chọn trang PDF với dropdown multiselect và navigation"""
    if not documents:
        st.info("📄 Chưa có tài liệu PDF nào để chọn trang.")
        return None, None, None, 0
    
    # Lọc chỉ PDF documents
    pdf_docs = [doc for doc in documents if doc.get('file_type', '').lower() == 'pdf' or 
                (hasattr(doc.get('file', {}), 'name') and doc['file'].name.lower().endswith('.pdf'))]
    
    if not pdf_docs:
        st.info("📄 Chưa có tài liệu PDF nào để chọn trang.")
        return None, None, None, 0
    
    # Row 1: Dropdown chọn PDF và Multiselect chọn trang
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Dropdown chọn PDF
        pdf_options = {}
        for i, doc in enumerate(pdf_docs):
            if hasattr(doc.get('file', {}), 'name'):
                # Document từ session_state (uploaded_documents)
                name = doc['file'].name
                pdf_options[f"{name} ({doc['file'].size} bytes)"] = doc
            else:
                # Document từ database (session_documents)
                name = doc.get('file_name', f'Document {i+1}')
                size = doc.get('file_size', 0)
                pdf_options[f"{name} ({size} bytes)"] = doc
        
        selected_pdf_name = st.selectbox(
            "📄 Chọn tài liệu PDF:",
            options=list(pdf_options.keys()),
            key="pdf_selector"
        )
        
        if not selected_pdf_name:
            return None, None, None, 0
        
        selected_doc = pdf_options[selected_pdf_name]
    
    with col2:
        # Lấy số trang của PDF
        page_count = 0
        if hasattr(selected_doc.get('file', {}), 'name'):
            # Document từ session_state
            page_count = doc_processor.get_pdf_page_count(selected_doc['file'])
        else:
            # Document từ database
            page_count = selected_doc.get('page_count', 0)
        
        if page_count <= 0:
            st.warning("⚠️ Không thể xác định số trang của PDF này.")
            return selected_doc, None, None, 0
        
        # Multiselect dropdown cho trang
        page_options = [f"Trang {i}" for i in range(1, page_count + 1)]
        selected_page_names = st.multiselect(
            f"📋 Chọn trang (tổng {page_count} trang):",
            options=page_options,
            key="page_multiselect",
            placeholder="Chọn trang để xem..."
        )
        
        # Convert page names thành numbers
        selected_pages = []
        if selected_page_names:
            selected_pages = [int(page.split()[-1]) for page in selected_page_names]
            selected_pages.sort()
    
    # Nếu không có trang nào được chọn
    if not selected_pages:
        st.info("👆 Hãy chọn ít nhất một trang để bắt đầu.")
        return selected_doc, None, None, 0
    
    # Determine current page to display
    if len(selected_pages) > 1:
        # Initialize current page index trong session state
        if "current_page_index" not in st.session_state:
            st.session_state.current_page_index = 0
        
        # Reset index nếu vượt quá số trang đã chọn
        if st.session_state.current_page_index >= len(selected_pages):
            st.session_state.current_page_index = 0
        
        # Trang hiện tại để hiển thị
        current_page_to_display = selected_pages[st.session_state.current_page_index]
    else:
        # Chỉ có 1 trang được chọn
        current_page_to_display = selected_pages[0]
    
    return selected_doc, current_page_to_display, selected_pages, st.session_state.get('current_page_index', 0)

def render_page_preview(doc_processor, selected_doc, selected_page, max_chars=300):
    """Hiển thị preview nội dung của trang đã chọn"""
    if not selected_doc or not selected_page:
        return None
    
    try:
        # Lấy nội dung trang
        page_content = None
        
        if hasattr(selected_doc.get('file', {}), 'name'):
            # Document từ session_state
            page_content = doc_processor.extract_specific_pdf_page(
                selected_doc['file'], 
                selected_page
            )
        else:
            # Document từ database - cần load từ document_pages table
            # (sẽ implement sau khi có database schema)
            page_content = f"Nội dung trang {selected_page} của {selected_doc.get('file_name', 'Document')}"
        
        if page_content:
            # Hiển thị preview
            st.subheader(f"👁️ Preview Trang {selected_page}")
            
            # Truncate nếu quá dài
            if len(page_content) > max_chars:
                preview = page_content[:max_chars] + "..."
                with st.expander("Xem đầy đủ nội dung trang"):
                    st.text_area(
                        "Nội dung đầy đủ:",
                        value=page_content,
                        height=300,
                        disabled=True,
                        key="full_page_content"
                    )
            else:
                preview = page_content
            
            st.text_area(
                "Nội dung trang:",
                value=preview,
                height=150,
                disabled=True,
                key="page_preview"
            )
            
            return page_content
        else:
            st.error(f"❌ Không thể tải nội dung trang {selected_page}")
            return None
            
    except Exception as e:
        st.error(f"❌ Lỗi khi tải preview: {str(e)}")
        return None

def render_tabbed_interface():
    """Render giao diện tabs cho chat trực tiếp và hỏi theo trang"""
    tab1, tab2 = st.tabs(["💬 Chat trực tiếp", "📄 Hỏi theo trang PDF"])
    
    return tab1, tab2

def render_page_chat_interface(page_content, selected_doc, selected_page):
    """Render giao diện chat riêng cho trang đã chọn"""
    if not page_content:
        st.warning("⚠️ Không có nội dung trang để chat.")
        return
    
    # Khởi tạo session state riêng cho page chat
    page_chat_key = f"page_chat_{selected_page}_{hash(str(selected_doc))}"
    
    if f"messages_{page_chat_key}" not in st.session_state:
        st.session_state[f"messages_{page_chat_key}"] = []
    
    # Hiển thị messages của page chat
    messages_container = st.container()
    with messages_container:
        for message in st.session_state[f"messages_{page_chat_key}"]:
            render_message(message)
    
    # Chat input cho page chat
    if prompt := st.chat_input(f"Hỏi về trang {selected_page}...", key=f"page_chat_input_{page_chat_key}"):
        # Kiểm tra đăng nhập
        if not (hasattr(st.session_state, 'user_id') and st.session_state.user_id):
            st.error("❌ Vui lòng đăng nhập để sử dụng chat!")
            return
        
        # Tạo session mới nếu cần (riêng cho page chat)
        page_session_id = None
        if not hasattr(st.session_state, f'page_session_{page_chat_key}'):
            # Tạo title cho page session - FIX: Handle both uploaded file và database document
            try:
                if hasattr(selected_doc, 'get'):
                    # Database document (dictionary)
                    doc_name = selected_doc.get('file_name', selected_doc.get('file', {}).get('name', 'Document'))
                elif hasattr(selected_doc, 'name'):
                    # Uploaded file object
                    doc_name = selected_doc.name
                else:
                    # Fallback
                    doc_name = 'Document'
            except:
                doc_name = 'Document'
                
            page_title = f"Trang {selected_page} - {doc_name}"
            
            page_session_id = st.session_state.chat_persistence.create_session(
                st.session_state.user_id,
                page_title
            )
            
            if page_session_id:
                st.session_state[f'page_session_{page_chat_key}'] = page_session_id
        else:
            page_session_id = st.session_state[f'page_session_{page_chat_key}']
        
        # Thêm user message
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        }
        st.session_state[f"messages_{page_chat_key}"].append(user_message)
        
        # Lưu user message vào database
        if page_session_id:
            st.session_state.chat_persistence.save_message(
                st.session_state.user_id,
                page_session_id,
                "user",
                prompt
            )
        
        # Hiển thị user message ngay
        with messages_container:
            render_message(user_message)
        
        # Tạo AI response dựa trên nội dung trang
        with st.spinner("🤖 Đang phân tích trang..."):
            if hasattr(st.session_state, 'doc_processor'):
                response = st.session_state.doc_processor.answer_question_with_openai(
                    prompt,
                    page_content
                )
            else:
                response = "Không thể xử lý câu hỏi. Vui lòng thử lại."
        
        # Thêm AI response
        ai_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        }
        st.session_state[f"messages_{page_chat_key}"].append(ai_message)
        
        # Lưu AI response vào database
        if page_session_id:
            st.session_state.chat_persistence.save_message(
                st.session_state.user_id,
                page_session_id,
                "assistant",
                response
            )
        
        st.rerun()

def render_document_info_card(doc):
    """Render thẻ thông tin tài liệu"""
    with st.container():
        st.markdown("""
        <div style="
            padding: 1rem;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: linear-gradient(135deg, #f8f9ff, #ffffff);
            margin: 0.5rem 0;
        ">
        """, unsafe_allow_html=True)
        
        # Thông tin cơ bản
        if hasattr(doc.get('file', {}), 'name'):
            # Document từ session_state
            st.markdown(f"**📄 {doc['file'].name}**")
            st.markdown(f"**Kích thước:** {doc['file'].size} bytes")
            if 'timestamp' in doc:
                st.markdown(f"**Thời gian upload:** {doc['timestamp'].strftime('%H:%M %d/%m/%Y')}")
        else:
            # Document từ database
            st.markdown(f"**📄 {doc.get('file_name', 'Unknown')}**")
            st.markdown(f"**Kích thước:** {doc.get('file_size', 0)} bytes")
            if 'created_at' in doc:
                st.markdown(f"**Thời gian upload:** {doc['created_at'].strftime('%H:%M %d/%m/%Y')}")
        
        # Thông tin bổ sung
        if doc.get('page_count'):
            st.markdown(f"**Số trang:** {doc['page_count']}")
        
        if doc.get('summary'):
            with st.expander("📝 Tóm tắt"):
                st.markdown(doc['summary'])
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_pdf_page_image_viewer(doc_processor, selected_doc, selected_page, selected_pages=None):
    """
    Render PDF page viewer với zoom controls và hiển thị ảnh
    
    Args:
        doc_processor: DocumentProcessor instance
        selected_doc: Document đã chọn
        selected_page: Số trang đã chọn
        selected_pages: Danh sách tất cả các trang đã chọn (optional)
    """
    if not selected_doc or not selected_page:
        st.warning("⚠️ Chưa chọn tài liệu hoặc trang.")
        return
    
    # Header với thông tin trang
    st.subheader(f"📄 Trang {selected_page}")
    
    # Zoom controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        zoom_level = st.selectbox(
            "🔍 Mức zoom:",
            options=[100, 125, 150, 200],
            index=1,  # Mặc định 125%
            key="pdf_zoom_level"
        )
    
    with col3:
        # Hiển thị kích thước gốc
        if hasattr(selected_doc.get('file', {}), 'name'):
            width, height = doc_processor.get_pdf_image_dimensions(
                selected_doc['file'], 
                selected_page
            )
    
    st.divider()
    
    # Hiển thị ảnh PDF
    try:
        # Get file object
        pdf_file = None
        if hasattr(selected_doc.get('file', {}), 'name'):
            pdf_file = selected_doc['file']
        else:
            st.warning("⚠️ Chỉ hiển thị được ảnh cho tài liệu vừa upload.")
            return
        
        # Convert DPI
        dpi = int(zoom_level * 1.5)  # Convert zoom % to DPI
        
        with st.spinner(f"🔄 Đang tải trang {selected_page} với zoom {zoom_level}%..."):
            # Lấy ảnh PDF
            pdf_image = doc_processor.extract_pdf_page_as_image(
                pdf_file, 
                selected_page, 
                dpi=dpi
            )
            
            if pdf_image:
                # Hiển thị ảnh với caption
                st.image(
                    pdf_image,
                    caption=f"Trang {selected_page} - Zoom {zoom_level}%",
                    use_container_width=True
                )
                
                
            else:
                st.error("❌ Không thể tải ảnh PDF. Vui lòng thử lại.")
                
    except Exception as e:
        st.error(f"❌ Lỗi khi hiển thị ảnh PDF: {str(e)}")
    
    # Navigation controls ngay dưới ảnh (nếu có nhiều trang)
    if selected_pages and len(selected_pages) > 1:
        st.divider()
        
        # Initialize current page index trong session state
        if "current_page_index" not in st.session_state:
            st.session_state.current_page_index = 0
        
        # Reset index nếu vượt quá số trang đã chọn
        if st.session_state.current_page_index >= len(selected_pages):
            st.session_state.current_page_index = 0
        
        # Tìm index của trang hiện tại
        try:
            current_index = selected_pages.index(selected_page)
            st.session_state.current_page_index = current_index
        except ValueError:
            pass  # Giữ nguyên index hiện tại nếu không tìm thấy
        
        # Navigation controls
        col_left, col_center, col_right = st.columns([1, 3, 1])
        
        with col_left:
            if st.button("◀", key="nav_left_image", disabled=(st.session_state.current_page_index <= 0)):
                st.session_state.current_page_index = max(0, st.session_state.current_page_index - 1)
                st.rerun()
        
        with col_center:
            current_page = selected_pages[st.session_state.current_page_index]
            st.markdown(f"<div style='text-align: center; padding: 8px;'>"
                       f"<strong>📄 Trang {current_page} ({st.session_state.current_page_index + 1}/{len(selected_pages)})</strong>"
                       f"</div>", unsafe_allow_html=True)
        
        with col_right:
            if st.button("▶", key="nav_right_image", disabled=(st.session_state.current_page_index >= len(selected_pages) - 1)):
                st.session_state.current_page_index = min(len(selected_pages) - 1, st.session_state.current_page_index + 1)
                st.rerun()
    
    # Modal toàn màn hình (nếu được yêu cầu)
    if st.session_state.get('show_fullscreen', False):
        render_fullscreen_pdf_modal(doc_processor, selected_doc, selected_page)

def render_fullscreen_pdf_modal(doc_processor, selected_doc, selected_page):
    """Hiển thị PDF trong modal toàn màn hình"""
    with st.expander("🖼️ Xem toàn màn hình", expanded=True):
        col1, col2 = st.columns([5, 1])
        
        with col2:
            if st.button("❌ Đóng", key="close_fullscreen"):
                st.session_state.show_fullscreen = False
                st.rerun()
        
        with col1:
            st.markdown("### 📄 Xem toàn màn hình")
        
        # Hiển thị ảnh với độ phân giải cao
        try:
            pdf_file = selected_doc['file']
            
            with st.spinner("🔄 Đang tải ảnh độ phân giải cao..."):
                # Sử dụng DPI cao cho fullscreen
                high_res_image = doc_processor.extract_pdf_page_as_image(
                    pdf_file, 
                    selected_page, 
                    dpi=200
                )
                
                if high_res_image:
                    st.image(
                        high_res_image,
                        caption=f"Trang {selected_page} - Độ phân giải cao",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Không thể tải ảnh độ phân giải cao.")
                    
        except Exception as e:
            st.error(f"❌ Lỗi khi hiển thị ảnh fullscreen: {str(e)}")

def render_page_summary_from_ocr(doc_processor, selected_doc, selected_page, max_chars=200):
    """
    Hiển thị tóm tắt ngắn gọn của trang từ OCR text
    
    Args:
        doc_processor: DocumentProcessor instance
        selected_doc: Document đã chọn
        selected_page: Số trang đã chọn
        max_chars: Số ký tự tối đa cho tóm tắt
    """
    try:
        # Lấy OCR text của trang
        if hasattr(selected_doc.get('file', {}), 'name'):
            page_content = doc_processor.extract_specific_pdf_page(
                selected_doc['file'], 
                selected_page
            )
        else:
            # Từ database - implement sau
            page_content = selected_doc.get('content', '')
        
        if page_content:
            # Tạo tóm tắt ngắn
            if len(page_content) > max_chars:
                summary = page_content[:max_chars] + "..."
            else:
                summary = page_content
            
            # Hiển thị trong info box
            st.info(f"📝 **Nội dung trang {selected_page}:**\n\n{summary}")
            
            # Nút xem đầy đủ
            with st.expander("👁️ Xem nội dung đầy đủ"):
                st.text_area(
                    "Nội dung OCR đầy đủ:",
                    value=page_content,
                    height=200,
                    disabled=True,
                    key=f"full_ocr_content_{selected_page}"
                )
                
                # Thống kê
                word_count = len(page_content.split())
                char_count = len(page_content)
                st.caption(f"📊 Thống kê: {word_count} từ, {char_count} ký tự")
        else:
            st.warning("⚠️ Không có nội dung OCR cho trang này.")
            
    except Exception as e:
        st.error(f"❌ Lỗi khi tải nội dung trang: {str(e)}")
