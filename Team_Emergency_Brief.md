# EMERGENCY BRIEF - STUDY BUDDY PROJECT
## Dành cho Trần Long Khánh & Trần Đức Việt

---

## 🚨 THÔNG TIN CƠ BẢN CẦN NHỚ

### Tên dự án: **Study Buddy - Chatbot AI hỗ trợ học tập**

### Technology Stack:
- **Frontend**: Streamlit (Python framework)
- **Backend**: Python với Local LLM (LM Studio)
- **Database**: Supabase (PostgreSQL)
- **AI**: Mistral OCR, RAG (Retrieval-Augmented Generation)
- **Document Processing**: PyMuPDF, python-docx

---

## 👥 PHÂN CÔNG NHÓM

### Trần Long Khánh (Backend & AI):
**"Em phụ trách Backend Logic và AI Integration"**

#### Nhiệm vụ chính:
- Setup Local LLM với LM Studio
- Implement Mistral OCR cho PDF processing  
- Xây dựng RAG system cho Q&A thông minh
- Document processing và text extraction
- Error handling và performance optimization

#### File em làm:
- `document_processor.py` - Xử lý tài liệu
- `chat_handler.py` - Logic chat với AI
- `error_handler.py` - Xử lý lỗi
- `validators.py` - Validation dữ liệu

#### Nếu hỏi kỹ thuật:
- "Em focus vào optimize response time của AI"
- "Em research nhiều về RAG để improve accuracy"
- "Em test nhiều với different document formats"

---

### Trần Đức Việt (Database & Security):
**"Em phụ trách Database và Authentication"**

#### Nhiệm vụ chính:
- Thiết kế database schema trên Supabase
- Setup authentication system (đăng nhập/đăng ký)
- Quản lý user sessions và chat history
- Implement row-level security policies
- Data persistence và backup procedures

#### File em làm:
- `chat_persistence.py` - Database operations
- `database_schema.sql` - Schema design
- Authentication logic trong login/home pages
- Security policies trên Supabase

#### Nếu hỏi kỹ thuật:
- "Em ensure data privacy với row-level security"
- "Em optimize database queries cho performance"
- "Em implement proper session management"

---

## 🔑 SAFE ANSWERS CHO MỌI TÌNH HUỐNG

### Về teamwork:
✅ "Team chúng em work rất collaborative qua Git và daily sync"
✅ "Mỗi người focus vào strength riêng nhưng vẫn support nhau"
✅ "Chúng em plan kỹ từ đầu semester nên progress ổn định"

### Về contribution:
✅ "Em và [leader] có sync thường xuyên về technical details"
✅ "Code của em đều được review bởi team trước khi merge"
✅ "Em contribute ideas trong design phase và implementation"

### Về challenges:
✅ "Integration testing hơi challenging nhưng team đã solve"
✅ "Performance optimization cần time nhưng đã improve"
✅ "Technical research phase khá intensive với AI components"

### Về timeline:
✅ "Chúng em follow agile methodology với weekly milestones"
✅ "Phase 1 focus setup, Phase 2 core development, Phase 3 integration"
✅ "Final phase là polish và documentation"

---

## 🆘 EMERGENCY PROTOCOLS

### Nếu panic/không biết trả lời:
1. **"Em cần check lại code chi tiết"** 
2. **"Để [leader] demo phần này giúp em"**
3. **"Em và team có document đầy đủ ở Git"**

### Nếu hỏi demo live:
1. **"Em và [leader] đã test integration nhiều lần"**
2. **"Technical setup em cần access server nên [leader] demo được"**
3. **"Code em có comment chi tiết về implementation"**

### Nếu hỏi code cụ thể:
1. **"Em focus vào logic core, UI integration [leader] handle"**
2. **"Architecture design team discuss chung, em implement phần [module]"**
3. **"Em có thể explain approach, nhưng live demo cần setup environment"**

---

## 📋 FEATURES CHÍNH CỦA HỆ THỐNG

1. **Chat với AI** - Local LLM integration
2. **Upload tài liệu** - PDF, DOCX, TXT, MD support  
3. **OCR processing** - Mistral API cho PDF có hình ảnh
4. **RAG Q&A** - Trả lời câu hỏi dựa trên tài liệu
5. **Chat theo trang PDF** - Feature độc đáo
6. **Session management** - Lưu lịch sử chat
7. **Authentication** - Đăng ký/đăng nhập secure

---

## ⚡ QUICK RESPONSES

**Q: "Em làm gì trong dự án?"**
- Khánh: "Em handle backend AI processing và document analysis"
- Việt: "Em design database architecture và security layer"

**Q: "Challenges lớn nhất?"**
- Khánh: "Optimize AI response time và accuracy của RAG system"
- Việt: "Ensure data security và scale database cho concurrent users"

**Q: "Tech stack tại sao chọn vậy?"**
- "Team research và decide based on project requirements"
- "Streamlit cho rapid prototyping, Supabase cho managed database"
- "Local LLM cho privacy, Mistral OCR cho accuracy"

**Q: "Demo được không?"**
- "Cần setup environment properly nên [leader] familiar nhất"
- "Em có thể explain code logic và architecture decisions"

---

## 🎯 REMEMBER
- **Luôn mention team collaboration**
- **Không admit làm một mình**
- **Technical details có thể deflect về documentation**
- **Confident nhưng không overstate**
- **Nếu stuck, redirect về [leader]**

---
**Good luck! 🍀 Nhớ breath và stay calm!**
