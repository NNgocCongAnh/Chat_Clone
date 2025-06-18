import streamlit as st
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from ..utils.document_processor import DocumentProcessor
from ..utils.chat_handler import ChatHandler
from ..utils.chat_persistence import ChatPersistence
from ..utils.ui_components import (
    render_message, render_sidebar, render_question_carousel, add_custom_css,
    render_tabbed_interface, render_page_selector, render_page_preview, 
    render_page_chat_interface, render_document_info_card,
    render_pdf_page_image_viewer, render_page_summary_from_ocr
)
from supabase import create_client

# Enhanced Home Page Design
# Author: Nguyễn Ngọc Công Anh - Frontend & UI/UX Enhancement

# Load environment variables
load_dotenv()

# Enhanced page configuration với custom styling
st.set_page_config(
    page_title="Study Buddy - AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Study Buddy v2.0\nPowered by AI for enhanced learning experience!"
    }
)

# Load CSS tùy chỉnh
def load_css():
    try:
        with open("assets/styles/style.css", encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except UnicodeDecodeError:
        # Fallback với encoding khác nếu UTF-8 không hoạt động
        with open("assets/styles/style.css", encoding='latin-1') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # File CSS không tồn tại - sử dụng CSS mặc định
        st.markdown("""
        <style>
        .main .block-container { padding-top: 1rem; }
        .stButton > button { border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)

# Khởi tạo session state
def init_session_state():
    # Khởi tạo Supabase connection
    if "supabase" not in st.session_state:
        # Đọc credentials từ environment variables
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        # Fallback nếu không có trong .env (để tương thích ngược)
        if not SUPABASE_URL:
            try:
                SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
                SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
            except Exception:
                st.error("❌ Chưa cấu hình Supabase credentials. Vui lòng kiểm tra file .env")
                st.stop()
        
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                st.success("✅ Đã kết nối Database (Supabase)")
            except Exception as e:
                st.error(f"❌ Lỗi kết nối Database: {str(e)}")
                st.stop()
        else:
            st.error("❌ Thiếu Supabase credentials. Vui lòng cấu hình trong file .env")
            st.stop()
    
    # Khởi tạo ChatPersistence
    if "chat_persistence" not in st.session_state:
        st.session_state.chat_persistence = ChatPersistence(st.session_state.supabase)
        # Test connection ngay khi khởi tạo
        st.session_state.chat_persistence.test_connection()
    
    # Session management
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "user_sessions" not in st.session_state:
        st.session_state.user_sessions = []
    if "session_loaded" not in st.session_state:
        st.session_state.session_loaded = False
    
    # Original states
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []
    if "chat_handler" not in st.session_state:
        st.session_state.chat_handler = ChatHandler()
    if "doc_processor" not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
    if "document_summary" not in st.session_state:
        st.session_state.document_summary = ""
    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = []
    if "document_embeddings" not in st.session_state:
        st.session_state.document_embeddings = []
    if "document_text" not in st.session_state:
        st.session_state.document_text = ""

def render_welcome_hero():
    """Render enhanced welcome hero section"""
    if not st.session_state.messages and not st.session_state.uploaded_documents:
        # Enhanced hero section với animations
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            color: white;
            position: relative;
            overflow: hidden;
        ">
            <div style="position: relative; z-index: 2;">
                <h1 style="font-size: 3rem; margin-bottom: 1rem; color: white;">
                    🎓 Study Buddy
                </h1>
                <h2 style="font-size: 1.5rem; margin-bottom: 2rem; opacity: 0.9; color: white;">
                    AI Learning Assistant được nâng cấp
                </h2>
                <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;">
                    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h3 style="color: white; margin: 0;">📚 Smart Document Analysis</h3>
                        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">AI-powered document understanding</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h3 style="color: white; margin: 0;">💬 Interactive Chat</h3>
                        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Natural conversation about your content</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h3 style="color: white; margin: 0;">🎯 Page-Specific Chat</h3>
                        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Focus on specific PDF pages</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start guide
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                border: 1px solid #e5e7eb;
            ">
                <h3 style="color: #667eea;">📋 Bước 1</h3>
                <p style="color: #6b7280;">Upload tài liệu PDF, DOCX, TXT hoặc MD từ sidebar</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                border: 1px solid #e5e7eb;
            ">
                <h3 style="color: #667eea;">💭 Bước 2</h3>
                <p style="color: #6b7280;">Chọn câu hỏi gợi ý hoặc đặt câu hỏi tự do</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                border: 1px solid #e5e7eb;
            ">
                <h3 style="color: #667eea;">🎯 Bước 3</h3>
                <p style="color: #6b7280;">Sử dụng tab "Hỏi theo trang" để chat với từng trang PDF</p>
            </div>
            """, unsafe_allow_html=True)

def render_enhanced_sidebar():
    """Enhanced sidebar với modern design"""
    with st.sidebar:
        # Custom header với gradient
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 1.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        ">
            <h2 style="margin: 0; color: white;">🎓 Study Buddy</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; color: white;">AI Learning Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User session management
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            # Enhanced user info section
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                padding: 1rem;
                border-radius: 12px;
                border: 1px solid #bae6fd;
                margin-bottom: 1rem;
            ">
                <p style="margin: 0; color: #0369a1; font-weight: 600;">👤 Đã đăng nhập</p>
                <small style="color: #0284c7;">Session được lưu tự động</small>
            </div>
            """, unsafe_allow_html=True)
            
            col2 = st.columns([4,4])[0]
            with col2:
                if st.button("🚪 Đăng xuất", use_container_width=True, type="secondary"):
                    # Reset tất cả session states
                    st.session_state.authenticated = False
                    st.session_state.user_id = None
                    st.session_state.current_session_id = None
                    st.session_state.user_sessions = []
                    st.session_state.session_loaded = False
                    st.session_state.messages = []
                    st.session_state.uploaded_documents = []
                    st.session_state.document_summary = ""
                    st.session_state.suggested_questions = []
                    st.session_state.document_text = ""
                    st.success("✅ Đã đăng xuất!")
                    st.rerun()

def main():
    # Enhanced CSS loading với fallback
    try:
        load_css()
        add_custom_css()
        
        # Additional inline CSS for enhanced UI
        st.markdown("""
        <style>
        /* Enhanced page styling */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
        }
        
        /* Enhanced tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: linear-gradient(90deg, #f8fafc, #f1f5f9);
            padding: 0.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Enhanced divider */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }
        
        /* Enhanced containers */
        .element-container {
            margin-bottom: 1rem;
        }
        
        /* Enhanced expander */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, #f8fafc, #ffffff);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: linear-gradient(90deg, #e2e8f0, #f8fafc);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        # Fallback CSS nếu file không tồn tại
        st.markdown("""
        <style>
        .main .block-container { padding-top: 1rem; }
        .stButton > button { border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Load user sessions nếu đã login
    if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
        if not st.session_state.session_loaded:
            st.session_state.user_sessions = st.session_state.chat_persistence.get_user_sessions(st.session_state.user_id)
            st.session_state.session_loaded = True
    
    # Enhanced sidebar
    render_enhanced_sidebar()
    
    # Continue with existing sidebar logic but with enhanced styling
    with st.sidebar:
        
        # Session Management
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            st.header("💾 Lịch sử Chat")
            
            # Nút tạo chat mới
            if st.button("➕ Chat mới", use_container_width=True):
                st.session_state.current_session_id = None
                st.session_state.messages = []
                st.session_state.document_summary = ""
                st.session_state.suggested_questions = []
                st.session_state.document_text = ""
                st.session_state.uploaded_documents = []
                st.rerun()
            
            st.divider()
            
            # Hiển thị danh sách sessions
            if st.session_state.user_sessions:
                st.subheader("📋 Cuộc trò chuyện")
                
                for session in st.session_state.user_sessions:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            # Hiển thị session với title và preview
                            session_display = f"**{session['title']}**"
                            if session['preview']:
                                session_display += f"\n*{session['preview']}*"
                            
                            # Thêm timestamp
                            now = datetime.now(timezone.utc)
                            # Ensure both datetimes are timezone-aware
                            if session['updated_at'].tzinfo is None:
                                updated_at = session['updated_at'].replace(tzinfo=timezone.utc)
                            else:
                                updated_at = session['updated_at']
                            
                            time_ago = now - updated_at
                            if time_ago.days > 0:
                                time_str = f"{time_ago.days} ngày trước"
                            elif time_ago.seconds > 3600:
                                time_str = f"{time_ago.seconds // 3600} giờ trước"
                            else:
                                time_str = f"{time_ago.seconds // 60} phút trước"
                            
                            session_display += f"\n🕐 {time_str}"
                            
                            # Button để load session
                            if st.button(
                                session_display,
                                key=f"session_{session['id']}",
                                use_container_width=True,
                                help="Click để tải cuộc trò chuyện này"
                            ):
                                # Load session
                                st.session_state.current_session_id = session['id']
                                st.session_state.messages = st.session_state.chat_persistence.load_session_messages(session['id'])
                                
                                # Reset document states when switching sessions
                                st.session_state.document_summary = ""
                                st.session_state.suggested_questions = []
                                st.session_state.document_text = ""
                                st.session_state.uploaded_documents = []
                                
                                st.success(f"✅ Đã tải: {session['title']}")
                                st.rerun()
                        
                        with col2:
                            # Nút xóa session
                            if st.button("🗑️", key=f"delete_session_{session['id']}", help="Xóa cuộc trò chuyện"):
                                if st.session_state.chat_persistence.delete_session(session['id'], st.session_state.user_id):
                                    # Refresh sessions list
                                    st.session_state.user_sessions = st.session_state.chat_persistence.get_user_sessions(st.session_state.user_id)
                                    
                                    # Nếu đang ở session bị xóa, reset
                                    if st.session_state.current_session_id == session['id']:
                                        st.session_state.current_session_id = None
                                        st.session_state.messages = []
                                    
                                    st.rerun()
                    
                    st.divider()
            else:
                st.info("Chưa có cuộc trò chuyện nào. Hãy bắt đầu chat!")
        
        st.header("📄 Upload Tài liệu")
        uploaded_file = st.file_uploader(
            "Chọn tài liệu",
            type=['pdf', 'docx', 'txt', 'md'],
            help="Hỗ trợ PDF, DOCX, TXT, MD"
        )
        
        if uploaded_file is not None:
            # Kiểm tra xem file đã được xử lý chưa bằng tên và kích thước
            file_already_processed = False
            for doc in st.session_state.uploaded_documents:
                if (doc["file"].name == uploaded_file.name and 
                    doc["file"].size == uploaded_file.size):
                    file_already_processed = True
                    break
            
            if not file_already_processed:
                with st.spinner("Đang xử lý tài liệu..."):
                    doc_content = st.session_state.doc_processor.process_document(uploaded_file)
                    if doc_content:
                        # Tóm tắt tài liệu
                        with st.spinner("Đang tóm tắt tài liệu..."):
                            summary = st.session_state.doc_processor.summarize_text(doc_content)
                            st.session_state.document_summary = summary
                        
                        # Tạo câu hỏi gợi ý
                        with st.spinner("Đang tạo câu hỏi gợi ý..."):
                            questions = st.session_state.doc_processor.generate_questions(doc_content)
                            st.session_state.suggested_questions = questions
                        
                        # Cache document text để tái sử dụng
                        st.session_state.document_text = doc_content
                        st.session_state.document_embeddings = []
                        
                        st.session_state.uploaded_documents.append({
                            "file": uploaded_file,
                            "content": doc_content,
                            "timestamp": datetime.now(),
                            "summary": summary,
                            "questions": questions
                        })
                        st.success(f"✅ Đã xử lý xong: {uploaded_file.name}")
        
        # Hiển thị tài liệu đã upload
        if st.session_state.uploaded_documents:
            st.header("📚 Tài liệu đã tải")
            for i, doc in enumerate(st.session_state.uploaded_documents):
                with st.expander(f"📄 {doc['file'].name}"):
                    st.write(f"**Kích thước:** {doc['file'].size} bytes")
                    st.write(f"**Thời gian:** {doc['timestamp'].strftime('%H:%M %d/%m/%Y')}")
                    st.write(f"**Nội dung:** {len(doc['content'])} ký tự")
                    
                    # Hiển thị tóm tắt
                    if 'summary' in doc and doc['summary']:
                        st.write("**📝 Tóm tắt:**")
                        st.info(doc['summary'])
                    else:
                        st.warning("Chưa có tóm tắt")
                    
                    if st.button(f"Xóa", key=f"delete_{i}"):
                        st.session_state.uploaded_documents.pop(i)
                        # Reset document-related states
                        st.session_state.document_summary = ""
                        st.session_state.suggested_questions = []
                        st.session_state.document_text = ""
                        st.rerun()
        
        # Nút xóa lịch sử chat
        if st.button("🗑️ Xóa lịch sử chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Enhanced main area với welcome hero
    render_welcome_hero()
    
    # Enhanced title section
    if st.session_state.messages or st.session_state.uploaded_documents:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                margin: 0;
            ">🎓 Study Buddy</h1>
            <p style="color: #6b7280; margin: 0.5rem 0 0 0;">AI Learning Assistant đang hoạt động</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced tabs with modern styling
    tab1, tab2 = render_tabbed_interface()
    
    # TAB 1: Chat trực tiếp (như cũ)
    with tab1:
        # Hiển thị tóm tắt tài liệu
        if st.session_state.document_summary:
            st.header("📝 Tóm tắt tài liệu")
            with st.container():
                st.markdown(f"**Tóm tắt:** {st.session_state.document_summary}")
            st.divider()
        
        # Container cho messages
        messages_container = st.container()
        
        # Hiển thị messages
        with messages_container:
            for message in st.session_state.messages:
                render_message(message)
        
        # Hiển thị carousel câu hỏi gợi ý NGAY TRƯỚC chat input
        if st.session_state.suggested_questions:
            render_question_carousel(st.session_state.suggested_questions, st.session_state.document_text)
        
        # Chat input cho tab 1
        if prompt := st.chat_input("Nhập tin nhắn của bạn...", key="main_chat_input"):
            # Kiểm tra nếu user đã login
            if not (hasattr(st.session_state, 'user_id') and st.session_state.user_id):
                st.error("❌ Vui lòng đăng nhập để sử dụng chat!")
                st.stop()
            
            # Lưu tài liệu vào database khi có session
            if st.session_state.uploaded_documents and st.session_state.current_session_id:
                for doc in st.session_state.uploaded_documents:
                    # Kiểm tra xem đã lưu chưa
                    if not hasattr(doc, 'saved_to_db'):
                        file_type = doc['file'].name.split('.')[-1].lower()
                        page_count = None
                        
                        # Lấy page count cho PDF
                        if file_type == 'pdf':
                            page_count = st.session_state.doc_processor.get_pdf_page_count(doc['file'])
                        
                        # Lưu vào database
                        document_id = st.session_state.chat_persistence.save_document_to_session(
                            st.session_state.user_id,
                            st.session_state.current_session_id,
                            doc['file'].name,
                            file_type,
                            doc['file'].size,
                            doc['content'],
                            doc.get('summary', ''),
                            doc.get('questions', []),
                            page_count
                        )
                        
                        if document_id:
                            doc['saved_to_db'] = True
                            doc['document_id'] = document_id
            
            # Tạo session mới nếu chưa có
            if not st.session_state.current_session_id:
                # Generate smart title từ message đầu tiên
                smart_title = st.session_state.chat_persistence.generate_smart_title(prompt)
                session_id = st.session_state.chat_persistence.create_session(
                    st.session_state.user_id, 
                    smart_title
                )
                
                if session_id:
                    st.session_state.current_session_id = session_id
                    # Refresh sessions list
                    st.session_state.user_sessions = st.session_state.chat_persistence.get_user_sessions(st.session_state.user_id)
                else:
                    st.error("❌ Không thể tạo session chat mới!")
                    st.stop()
            
            # Thêm tin nhắn của user vào UI
            user_message = {
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now()
            }
            st.session_state.messages.append(user_message)
            
            # Lưu user message vào database
            st.session_state.chat_persistence.save_message(
                st.session_state.user_id,
                st.session_state.current_session_id,
                "user",
                prompt
            )
            
            # Hiển thị tin nhắn user ngay lập tức
            with messages_container:
                render_message(user_message)
            
            # Xử lý phản hồi AI
            with st.spinner("Đang suy nghĩ..."):
                # Nếu có document thì dùng OpenAI, không thì dùng ChatHandler
                if st.session_state.document_text:
                    response = st.session_state.doc_processor.answer_question_with_openai(
                        prompt,
                        st.session_state.document_text
                    )
                else:
                    # Fallback cho chat thông thường
                    response = st.session_state.chat_handler.generate_response(
                        prompt, 
                        st.session_state.messages[:-1],
                        ""
                    )
                
                # Thêm phản hồi AI vào UI
                ai_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                }
                st.session_state.messages.append(ai_message)
                
                # Lưu AI response vào database
                st.session_state.chat_persistence.save_message(
                    st.session_state.user_id,
                    st.session_state.current_session_id,
                    "assistant",
                    response
                )
            
            # Rerun để hiển thị tin nhắn AI
            st.rerun()
    
    # TAB 2: Hỏi theo trang PDF
    with tab2:
        st.header("📄 Chat với trang PDF cụ thể")
        st.markdown("Chọn tài liệu PDF và trang cụ thể để chat riêng biệt.")
        
        # Kiểm tra đăng nhập
        if not (hasattr(st.session_state, 'user_id') and st.session_state.user_id):
            st.warning("⚠️ Vui lòng đăng nhập để sử dụng tính năng này.")
            return
        
        # Combine uploaded documents và documents từ database
        all_documents = []
        
        # Thêm documents từ session_state
        all_documents.extend(st.session_state.uploaded_documents)
        
        # Thêm documents từ database (nếu có session)
        if st.session_state.current_session_id:
            try:
                session_docs = st.session_state.chat_persistence.load_session_documents(
                    st.session_state.current_session_id
                )
                all_documents.extend(session_docs)
            except Exception as e:
                st.error(f"❌ Lỗi load documents từ database: {str(e)}")
        
        # Selector để chọn PDF và trang
        selected_doc, selected_page, selected_pages, current_page_index = render_page_selector(
            all_documents, 
            st.session_state.doc_processor
        )
        
        if selected_doc and selected_page:
            # Hiển thị thông tin tài liệu ngắn gọn
            render_document_info_card(selected_doc)
            
            st.divider()
            
            # Layout 2 cột: Trái (PDF Image), Phải (Tóm tắt + Chat)
            col_image, col_chat = st.columns([1, 1])  # 50-50 split
            
            with col_image:
                # PDF Image Viewer với navigation controls dưới ảnh
                render_pdf_page_image_viewer(
                    st.session_state.doc_processor,
                    selected_doc,
                    selected_page,
                    selected_pages  # Truyền thêm selected_pages
                )
            
            with col_chat:
                # Tóm tắt trang từ OCR
                st.subheader("📝 Nội dung trang")
                render_page_summary_from_ocr(
                    st.session_state.doc_processor,
                    selected_doc,
                    selected_page,
                    max_chars=300
                )
                
                st.divider()
                
                # Chat interface cho trang cụ thể
                if selected_pages and len(selected_pages) > 1:
                    st.subheader(f"💬 Chat về các trang đã chọn")
                    st.caption(f"Đang chat với {len(selected_pages)} trang: {', '.join([f'Trang {p}' for p in selected_pages])}")
                    
                    # Lấy nội dung tất cả các trang đã chọn
                    all_pages_content = ""
                    try:
                        # FIX: Check if selected_doc has 'file' attribute (uploaded document)
                        if hasattr(selected_doc, 'get') and hasattr(selected_doc.get('file', {}), 'name'):
                            # Document từ session_state (uploaded_documents)
                            for page_num in selected_pages:
                                page_content = st.session_state.doc_processor.extract_specific_pdf_page(
                                    selected_doc['file'], 
                                    page_num
                                )
                                if page_content:
                                    all_pages_content += f"\n\n=== TRANG {page_num} ===\n{page_content}"
                        elif hasattr(selected_doc, 'get'):
                            # Document từ database - implement sau
                            all_pages_content = selected_doc.get('content', '')
                        else:
                            # Fallback - có thể là UploadedFile trực tiếp
                            st.warning("⚠️ Không thể xử lý loại tài liệu này cho nhiều trang.")
                    except Exception as e:
                        st.error(f"❌ Lỗi khi lấy nội dung các trang: {str(e)}")
                    
                    if all_pages_content:
                        # Tạo key cho chat nhiều trang
                        multi_page_key = f"multi_page_{'_'.join(map(str, selected_pages))}"
                        render_page_chat_interface(
                            all_pages_content,
                            selected_doc,
                            multi_page_key  # Sử dụng key đặc biệt cho nhiều trang
                        )
                    else:
                        st.warning("⚠️ Không thể lấy nội dung các trang để chat.")
                else:
                    st.subheader(f"💬 Chat về trang {selected_page}")
                    
                    # Lấy page content để chat
                    page_content = None
                    try:
                        # FIX: Check if selected_doc has proper structure
                        if hasattr(selected_doc, 'get') and hasattr(selected_doc.get('file', {}), 'name'):
                            # Document từ session_state (uploaded_documents)
                            page_content = st.session_state.doc_processor.extract_specific_pdf_page(
                                selected_doc['file'], 
                                selected_page
                            )
                        elif hasattr(selected_doc, 'get'):
                            # Document từ database - implement sau
                            page_content = selected_doc.get('content', '')
                        else:
                            # Fallback
                            st.warning("⚠️ Không thể xử lý loại tài liệu này.")
                    except Exception as e:
                        st.error(f"❌ Lỗi khi lấy nội dung trang: {str(e)}")
                    
                    if page_content:
                        render_page_chat_interface(
                            page_content,
                            selected_doc,
                            selected_page
                        )
                    else:
                        st.warning("⚠️ Không thể lấy nội dung trang để chat.")
        else:
            if not all_documents:
                st.info("📄 Chưa có tài liệu PDF nào. Hãy upload PDF trong tab 'Chat trực tiếp' trước.")
            else:
                st.info("👆 Hãy chọn tài liệu PDF và trang để bắt đầu chat.")
