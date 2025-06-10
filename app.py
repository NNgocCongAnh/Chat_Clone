import streamlit as st
import os
from datetime import datetime
from utils.document_processor import DocumentProcessor
from utils.chat_handler import ChatHandler
from utils.ui_components import render_message, render_sidebar

# Cấu hình trang
st.set_page_config(
    page_title="ChatGPT Clone",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS tùy chỉnh
def load_css():
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Khởi tạo session state
def init_session_state():
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

def main():
    # Load CSS và khởi tạo
    try:
        load_css()
    except FileNotFoundError:
        pass  # CSS file chưa tồn tại
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("💬 ChatGPT Clone")
        
        # Upload tài liệu
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
    
    # Main chat area
    st.title("ChatGPT Clone với Upload Tài liệu")
    
    # Hiển thị tóm tắt và câu hỏi gợi ý
    if st.session_state.document_summary:
        st.header("📝 Tóm tắt tài liệu")
        with st.container():
            st.markdown(f"**Tóm tắt:** {st.session_state.document_summary}")
        
        st.header("❓ Câu hỏi gợi ý")
        if st.session_state.suggested_questions:
            col1, col2 = st.columns(2)
            for i, question in enumerate(st.session_state.suggested_questions):
                with col1 if i % 2 == 0 else col2:
                    if st.button(f"💬 {question}", key=f"question_{i}", use_container_width=True):
                        # Khi user click vào câu hỏi, tự động gửi câu hỏi đó
                        st.session_state.messages.append({
                            "role": "user",
                            "content": question,
                            "timestamp": datetime.now()
                        })
                        
                        # Sử dụng BART để trả lời dựa trên cached document text
                        response = st.session_state.doc_processor.answer_question_with_bart(
                            question,
                            st.session_state.document_text
                        )
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now()
                        })
                        st.rerun()
        
        st.divider()
    
    # Container cho messages
    messages_container = st.container()
    
    # Hiển thị messages
    with messages_container:
        for message in st.session_state.messages:
            render_message(message)
    
    # Chat input
    if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
        # Thêm tin nhắn của user
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Hiển thị tin nhắn user ngay lập tức
        with messages_container:
            render_message(user_message)
        
        # Xử lý phản hồi AI
        with st.spinner("Đang suy nghĩ..."):
            # Nếu có document thì dùng BART, không thì dùng ChatHandler
            if st.session_state.document_text:
                response = st.session_state.doc_processor.answer_question_with_bart(
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
            
            # Thêm phản hồi AI
            ai_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            }
            st.session_state.messages.append(ai_message)
        
        # Rerun để hiển thị tin nhắn AI
        st.rerun()

if __name__ == "__main__":
    main()
