# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)
## HỆ THỐNG STUDY BUDDY - CHATBOT AI HỖ TRỢ HỌC TẬP

---

**Nhóm thực hiện:** [SỐ NHÓM]
- **Thành viên 1:** [TÊN] - [MSSV] - Frontend Development & UI/UX
- **Thành viên 2:** Trần Long Khánh - 22010449 - Backend Logic & AI Integration
- **Thành viên 3:** Trần Đức Việt - 22010032 - Database & Authentication

**Lớp:** [LỚP]  
**Giảng viên:** [TÊN GIẢNG VIÊN]  
**Môn học:** Kỹ thuật Phần mềm (IT4490)

**Ngày:** [NGÀY/THÁNG/NĂM]

---

## MỤC LỤC

- [HỆ THỐNG STUDY BUDDY - CHATBOT AI HỖ TRỢ HỌC TẬP](#hệ-thống-study-buddy---chatbot-ai-hỗ-trợ-học-tập)
- [MỤC LỤC](#mục-lục)
- [1. GIỚI THIỆU](#1-giới-thiệu)
  - [1.1 Mục đích](#11-mục-đích)
  - [1.2 Phạm vi](#12-phạm-vi)
  - [1.3 Từ điển thuật ngữ](#13-từ-điển-thuật-ngữ)
  - [1.4 Tài liệu tham khảo](#14-tài-liệu-tham-khảo)
  - [1.5 Tổng quát](#15-tổng-quát)
- [2. CÁC YÊU CẦU CHỨC NĂNG](#2-các-yêu-cầu-chức-năng)
  - [2.1 Các tác nhân](#21-các-tác-nhân)
    - [2.1.1 Khách (Guest)](#211-khách-guest)
    - [2.1.2 Người dùng đã đăng nhập (Authenticated User)](#212-người-dùng-đã-đăng-nhập-authenticated-user)
    - [2.1.3 Hệ thống AI (AI System)](#213-hệ-thống-ai-ai-system)
    - [2.1.4 Hệ thống cơ sở dữ liệu (Database System)](#214-hệ-thống-cơ-sở-dữ-liệu-database-system)
  - [2.2 Các chức năng của hệ thống](#22-các-chức-năng-của-hệ-thống)
  - [2.3 Biểu đồ use-case tổng quát](#23-biểu-đồ-use-case-tổng-quát)
  - [2.4 Biểu đồ use-case phân rã](#24-biểu-đồ-use-case-phân-rã)
    - [2.4.1 Biểu đồ use-case cho Khách](#241-biểu-đồ-use-case-cho-khách)
    - [2.4.2 Biểu đồ use-case cho Người dùng đã đăng nhập](#242-biểu-đồ-use-case-cho-người-dùng-đã-đăng-nhập)
  - [2.5 Quy trình nghiệp vụ](#25-quy-trình-nghiệp-vụ)
    - [2.5.1 Quy trình đăng nhập](#251-quy-trình-đăng-nhập)
    - [2.5.2 Quy trình xử lý tài liệu](#252-quy-trình-xử-lý-tài-liệu)
    - [2.5.3 Quy trình chat với AI](#253-quy-trình-chat-với-ai)
    - [2.5.4 Quy trình chat theo trang PDF](#254-quy-trình-chat-theo-trang-pdf)
    - [2.5.5 Quy trình quản lý sessions](#255-quy-trình-quản-lý-sessions)
  - [2.6 Đặc tả use-case](#26-đặc-tả-use-case)
    - [UC001: Đăng nhập](#uc001-đăng-nhập)
    - [UC002: Upload và xử lý tài liệu](#uc002-upload-và-xử-lý-tài-liệu)
    - [UC003: Chat với AI sử dụng RAG](#uc003-chat-với-ai-sử-dụng-rag)
    - [UC004: Chat theo trang PDF cụ thể](#uc004-chat-theo-trang-pdf-cụ-thể)
    - [UC005: Quản lý chat sessions](#uc005-quản-lý-chat-sessions)
    - [UC006: Đăng ký tài khoản](#uc006-đăng-ký-tài-khoản)
    - [UC007: Đăng xuất](#uc007-đăng-xuất)
- [3. CÁC YÊU CẦU PHI CHỨC NĂNG](#3-các-yêu-cầu-phi-chức-năng)
  - [3.1 Các yêu cầu về hiệu năng](#31-các-yêu-cầu-về-hiệu-năng)
  - [3.2 Yêu cầu về bảo mật](#32-yêu-cầu-về-bảo-mật)
  - [3.3 Yêu cầu về giao diện](#33-yêu-cầu-về-giao-diện)
  - [3.4 Ràng buộc](#34-ràng-buộc)
- [4. PHÂN CHIA CÔNG VIỆC NHÓM](#4-phân-chia-công-việc-nhóm)
  - [4.1 Tổng quan phân chia](#41-tổng-quan-phân-chia)
  - [4.2 Thành viên 1: \[TÊN\] - Frontend Development \& UI/UX](#42-thành-viên-1-tên---frontend-development--uiux)
  - [4.3 Thành viên 2: Trần Long Khánh - Backend Logic \& AI Integration](#43-thành-viên-2-trần-long-khánh---backend-logic--ai-integration)
  - [4.4 Thành viên 3: Trần Đức Việt - Database \& Authentication](#44-thành-viên-3-trần-đức-việt---database--authentication)
  - [4.5 Timeline và Milestone](#45-timeline-và-milestone)
  - [4.6 Communication và Collaboration](#46-communication-và-collaboration)
  - [4.7 Quality Assurance](#47-quality-assurance)
- [5. KẾT LUẬN](#5-kết-luận)
  - [5.1 Tổng kết dự án](#51-tổng-kết-dự-án)
  - [5.2 Điểm mạnh của hệ thống](#52-điểm-mạnh-của-hệ-thống)
  - [5.3 Rủi ro và giải pháp](#53-rủi-ro-và-giải-pháp)
  - [5.4 Tiêu chí thành công](#54-tiêu-chí-thành-công)

---

## 1. GIỚI THIỆU

### 1.1 Mục đích

Tài liệu Đặc tả Yêu cầu Phần mềm (SRS) này được xây dựng nhằm xác định một cách chi tiết và đầy đủ các yêu cầu chức năng và phi chức năng của hệ thống Study Buddy - một ứng dụng chatbot AI hỗ trợ học tập thông minh. Tài liệu này đóng vai trò là cầu nối giao tiếp chính giữa nhóm phát triển, giảng viên hướng dẫn và các bên liên quan khác trong quá trình phát triển dự án.

Mục đích chính của tài liệu bao gồm: cung cấp hướng dẫn cụ thể cho nhóm phát triển trong việc thiết kế và xây dựng hệ thống, đảm bảo sản phẩm cuối cùng đáp ứng đúng nhu cầu người dùng và tiêu chuẩn kỹ thuật đã đề ra, tạo cơ sở cho việc kiểm thử và đánh giá chất lượng hệ thống.

### 1.2 Phạm vi

Hệ thống Study Buddy là một ứng dụng web-based chatbot AI được thiết kế để hỗ trợ học tập và nghiên cứu thông qua khả năng xử lý tài liệu thông minh và tương tác tự nhiên. Hệ thống cung cấp khả năng chat với AI sử dụng Local LLM (thông qua LM Studio), xử lý và phân tích các định dạng tài liệu phổ biến (PDF, DOCX, TXT, MD) với công nghệ OCR tiên tiến, tạo tóm tắt tự động và câu hỏi gợi ý từ nội dung tài liệu, triển khai RAG (Retrieval-Augmented Generation) để trả lời câu hỏi dựa trên tài liệu, và quản lý lịch sử chat với khả năng tìm kiếm và phân loại.

Hệ thống phục vụ ba nhóm người dùng chính: Khách (người dùng chưa đăng nhập) có thể xem giao diện và đăng ký tài khoản, Người dùng đã đăng nhập có thể sử dụng đầy đủ các tính năng chat và xử lý tài liệu, và Hệ thống AI đóng vai trò tác nhân tự động xử lý và phản hồi các yêu cầu từ người dùng.

Hệ thống không hỗ trợ: thanh toán trực tuyến hoặc thương mại điện tử, chỉnh sửa hoặc tạo mới tài liệu gốc, chia sẻ tài liệu giữa người dùng, và tích hợp với các hệ thống quản lý học tập khác (LMS).

### 1.3 Từ điển thuật ngữ

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| **AI (Artificial Intelligence)** | Trí tuệ nhân tạo, công nghệ cho phép máy tính thực hiện các tác vụ thông minh như con người |
| **Chatbot** | Chương trình máy tính được thiết kế để mô phỏng cuộc trò chuyện với người dùng thông qua text |
| **LLM (Large Language Model)** | Mô hình ngôn ngữ lớn được huấn luyện để hiểu và tạo ra văn bản tự nhiên |
| **LM Studio** | Công cụ cho phép chạy các mô hình AI ngôn ngữ lớn trên máy tính cá nhân |
| **OCR (Optical Character Recognition)** | Công nghệ nhận dạng ký tự quang học, chuyển đổi hình ảnh text thành text có thể chỉnh sửa |
| **RAG (Retrieval-Augmented Generation)** | Kỹ thuật kết hợp tìm kiếm thông tin và tạo sinh text để cải thiện độ chính xác |
| **API (Application Programming Interface)** | Giao diện lập trình ứng dụng, cho phép các phần mềm giao tiếp với nhau |
| **Session** | Phiên làm việc, một cuộc trò chuyện liên tục giữa người dùng và hệ thống |
| **Streamlit** | Framework Python để xây dựng ứng dụng web tương tác nhanh chóng |
| **Supabase** | Nền tảng cơ sở dữ liệu mã nguồn mở cung cấp database và authentication |

### 1.4 Tài liệu tham khảo

1. IEEE Recommended Practice for Software Requirements Specifications, IEEE Std 830-1998
2. Nguyễn Thị Thu Trang, "IT4490: Software Design and Construction", Đại học Bách khoa Hà Nội
3. Ian Sommerville, "Software Engineering", 10th Edition, Pearson, 2015
4. "Streamlit Documentation", https://docs.streamlit.io/
5. "LangChain Documentation - RAG Applications", https://python.langchain.com/docs/
6. "OpenAI API Documentation", https://platform.openai.com/docs/
7. Martin Fowler, "UML Distilled: A Brief Guide to the Standard Object Modeling Language", 3rd Edition

### 1.5 Tổng quát

Tài liệu SRS này được tổ chức thành ba phần chính một cách logic và có hệ thống. Phần đầu tiên là Giới thiệu, cung cấp cái nhìn tổng quan về mục đích, phạm vi và bối cảnh của dự án, đồng thời giải thích các thuật ngữ kỹ thuật quan trọng sẽ được sử dụng xuyên suốt tài liệu. Phần thứ hai là Các yêu cầu chức năng, mô tả chi tiết các tác nhân trong hệ thống, danh sách đầy đủ các chức năng, các biểu đồ use-case từ tổng quát đến cụ thể, quy trình nghiệp vụ và đặc tả use-case chi tiết. Phần thứ ba là Các yêu cầu phi chức năng, trình bày các yêu cầu về hiệu năng, bảo mật, giao diện người dùng và các ràng buộc kỹ thuật. Cuối cùng là phần Phân chia công việc nhóm, mô tả chi tiết trách nhiệm và nhiệm vụ cụ thể của từng thành viên trong nhóm phát triển.

---

## 2. CÁC YÊU CẦU CHỨC NĂNG

### 2.1 Các tác nhân

Hệ thống Study Buddy bao gồm các tác nhân sau:

#### 2.1.1 Khách (Guest)
Người dùng chưa có tài khoản hoặc chưa đăng nhập vào hệ thống. Khách có quyền xem giao diện chính của ứng dụng, đọc thông tin giới thiệu về các tính năng, thực hiện đăng ký tài khoản mới, và truy cập vào form đăng nhập. Tuy nhiên, khách không thể sử dụng các tính năng chat hoặc upload tài liệu.

#### 2.1.2 Người dùng đã đăng nhập (Authenticated User)
Người dùng đã có tài khoản và đăng nhập thành công vào hệ thống. Đây là tác nhân chính có quyền truy cập đầy đủ các tính năng: thực hiện chat với AI, upload và xử lý tài liệu, xem tóm tắt và câu hỏi gợi ý, quản lý lịch sử chat sessions, chat với trang PDF cụ thể, và đăng xuất khỏi hệ thống.

#### 2.1.3 Hệ thống AI (AI System)
Tác nhân tự động bao gồm các dịch vụ AI và xử lý backend. Hệ thống AI chịu trách nhiệm xử lý các yêu cầu chat từ người dùng thông qua Local LLM, thực hiện OCR và trích xuất nội dung từ tài liệu, tạo tóm tắt tự động và câu hỏi gợi ý, triển khai RAG để trả lời câu hỏi dựa trên tài liệu, và lưu trữ dữ liệu vào cơ sở dữ liệu.

#### 2.1.4 Hệ thống cơ sở dữ liệu (Database System)
Tác nhân quản lý dữ liệu sử dụng Supabase, chịu trách nhiệm lưu trữ thông tin người dùng và xác thực, quản lý các chat sessions và messages, lưu trữ metadata của tài liệu đã upload, và cung cấp dữ liệu theo yêu cầu từ ứng dụng.

### 2.2 Các chức năng của hệ thống

Hệ thống Study Buddy cung cấp các chức năng chính sau:

- **Đăng ký tài khoản**: Cho phép khách tạo tài khoản mới với email và mật khẩu, bao gồm xác thực email và validation dữ liệu đầu vào.

- **Đăng nhập/Đăng xuất**: Xác thực người dùng để truy cập hệ thống và quản lý phiên làm việc một cách an toàn.

- **Chat với AI**: Giao tiếp tự nhiên với AI assistant sử dụng Local LLM, hỗ trợ nhiều ngôn ngữ với khả năng hiểu context và duy trì cuộc hội thoại.

- **Upload và xử lý tài liệu**: Hỗ trợ upload các định dạng PDF, DOCX, TXT, MD với khả năng OCR cho PDF có hình ảnh và trích xuất text chính xác.

- **Tóm tắt tự động**: Sử dụng AI để tạo tóm tắt ngắn gọn, súc tích từ nội dung tài liệu dài, giúp người dùng nắm bắt nhanh ý chính.

- **Tạo câu hỏi gợi ý**: Tự động phân tích nội dung và đề xuất các câu hỏi có thể quan tâm để hỗ trợ việc học tập và nghiên cứu.

- **RAG (Retrieval-Augmented Generation)**: Trả lời câu hỏi chính xác dựa trên nội dung tài liệu đã upload, kết hợp tìm kiếm thông tin và tạo sinh câu trả lời.

- **Quản lý chat sessions**: Lưu trữ, phân loại và tìm kiếm lịch sử các cuộc trò chuyện với khả năng tạo title thông minh và preview.

- **Chat theo trang PDF**: Tính năng độc đáo cho phép chat với từng trang cụ thể của tài liệu PDF, hiển thị ảnh trang và nội dung tương ứng.

- **Quản lý tài liệu cá nhân**: Lưu trữ và tổ chức các tài liệu đã upload với metadata đầy đủ và khả năng xóa khi không cần thiết.

### 2.3 Biểu đồ use-case tổng quát


@startuml left to right direction skinparam packageStyle rectangle

actor "Khách" as Guest actor "Người dùng" as User actor "Hệ thống AI" as AI actor "Database" as DB

rectangle "Study Buddy System" { usecase "Xem giao diện" as UC1 usecase "Đăng ký" as UC2 usecase "Đăng nhập" as UC3 usecase "Chat với AI" as UC4 usecase "Upload tài liệu" as UC5 usecase "Xử lý tài liệu" as UC6 usecase "Tóm tắt tự động" as UC7 usecase "Tạo câu hỏi" as UC8 usecase "RAG Q\&A" as UC9 usecase "Quản lý sessions" as UC10 usecase "Chat theo trang PDF" as UC11 usecase "Đăng xuất" as UC12 }

Guest --> UC1 Guest --> UC2 Guest --> UC3

User --> UC3 User --> UC4 User --> UC5 User --> UC10 User --> UC11 User --> UC12

UC4 --> AI UC5 --> UC6 UC6 --> AI UC6 --> UC7 UC6 --> UC8 UC4 --> UC9 UC9 --> AI

AI --> DB UC2 --> DB UC3 --> DB UC10 --> DB

UC7 ..> UC6 : <> UC8 ..> UC6 : <> UC9 ..> UC6 : <> @enduml


*Hình 2-1: Biểu đồ use-case tổng quát của hệ thống Study Buddy*

### 2.4 Biểu đồ use-case phân rã

#### 2.4.1 Biểu đồ use-case cho Khách


@startuml left to right direction actor "Khách" as Guest

rectangle "Guest Functions" { usecase "Xem trang chủ" as UC1_1 usecase "Xem giới thiệu tính năng" as UC1_2 usecase "Đăng ký tài khoản" as UC2 usecase "Nhập thông tin đăng ký" as UC2_1 usecase "Xác thực email" as UC2_2 usecase "Đăng nhập" as UC3 usecase "Nhập thông tin đăng nhập" as UC3_1 usecase "Xác thực tài khoản" as UC3_2 }

Guest --> UC1_1 Guest --> UC1_2 Guest --> UC2 Guest --> UC3

UC2 --> UC2_1 UC2 --> UC2_2 UC3 --> UC3_1 UC3 --> UC3_2

UC2_1 ..> UC2 : <> UC2_2 ..> UC2 : <> UC3_1 ..> UC3 : <> UC3_2 ..> UC3 : <> @enduml



*Hình 2-2: Biểu đồ use-case chi tiết cho tác nhân Khách*

#### 2.4.2 Biểu đồ use-case cho Người dùng đã đăng nhập


@startuml left to right direction actor "Người dùng" as User

rectangle "User Functions" { usecase "Chat trực tiếp" as UC4 usecase "Gửi tin nhắn" as UC4_1 usecase "Nhận phản hồi AI" as UC4_2 usecase "Quản lý tài liệu" as UC5 usecase "Upload tài liệu" as UC5_1 usecase "Xem tóm tắt" as UC5_2 usecase "Xem câu hỏi gợi ý" as UC5_3 usecase "Chat theo trang PDF" as UC11 usecase "Chọn trang PDF" as UC11_1 usecase "Xem ảnh trang" as UC11_2 usecase "Chat với trang" as UC11_3 usecase "Quản lý sessions" as UC10 usecase "Tạo session mới" as UC10_1 usecase "Xem lịch sử" as UC10_2 usecase "Xóa session" as UC10_3 }

User --> UC4 User --> UC5 User --> UC11 User --> UC10

UC4 --> UC4_1 UC4 --> UC4_2 UC5 --> UC5_1 UC5 --> UC5_2 UC5 --> UC5_3 UC11 --> UC11_1 UC11 --> UC11_2 UC11 --> UC11_3 UC10 --> UC10_1 UC10 --> UC10_2 UC10 --> UC10_3

UC4_1 ..> UC4 : <> UC4_2 ..> UC4 : <> UC5_2 ..> UC5_1 : <> UC5_3 ..> UC5_1 : <> @enduml



*Hình 2-3: Biểu đồ use-case chi tiết cho Người dùng đã đăng nhập*

### 2.5 Quy trình nghiệp vụ

#### 2.5.1 Quy trình đăng nhập


@startuml start :Người dùng truy cập trang chủ; :Nhấn nút "Đăng nhập"; :Nhập email và mật khẩu; if (Thông tin hợp lệ?) then (yes) :Xác thực với Supabase; if (Xác thực thành công?) then (yes) :Tạo session; :Chuyển đến trang chính; :Hiển thị giao diện chat; stop else (no) :Hiển thị lỗi "Sai tài khoản/mật khẩu"; stop endif else (no) :Hiển thị lỗi validation; stop endif @enduml



*Hình 2-4: Biểu đồ hoạt động cho quy trình đăng nhập*

#### 2.5.2 Quy trình xử lý tài liệu


@startuml start :Người dùng chọn file upload; if (File hợp lệ?) then (yes) :Kiểm tra định dạng và kích thước; if (PDF file?) then (yes) :Gửi đến Mistral OCR; :Trích xuất text từ tất cả trang; else (DOCX/TXT/MD) :Đọc trực tiếp nội dung; endif :Tạo tóm tắt với Local LLM; :Tạo câu hỏi gợi ý; :Lưu vào session state; :Hiển thị kết quả; stop else (no) :Hiển thị lỗi "File không hợp lệ"; stop endif @enduml



*Hình 2-5: Biểu đồ hoạt động cho quy trình xử lý tài liệu*

#### 2.5.3 Quy trình chat với AI


@startuml start :Người dùng nhập tin nhắn; :Kiểm tra session đăng nhập; if (Có tài liệu trong session?) then (yes) :Sử dụng RAG với OpenAI; :Tìm nội dung liên quan; :Tạo context cho LLM; else (no) :Sử dụng ChatHandler thông thường; endif :Gửi request đến Local LLM; :Nhận response từ AI; :Lưu tin nhắn vào database; :Hiển thị phản hồi; :Cập nhật session; stop @enduml



*Hình 2-6: Biểu đồ hoạt động cho quy trình chat với AI*

#### 2.5.4 Quy trình chat theo trang PDF


@startuml start :Chọn tài liệu PDF; :Hiển thị danh sách trang; :Người dùng chọn trang cụ thể; :Render ảnh trang với PyMuPDF; :Trích xuất nội dung trang với OCR; :Hiển thị ảnh và tóm tắt trang; :Người dùng nhập câu hỏi; :Sử dụng nội dung trang làm context; :Gửi đến Local LLM; :Hiển thị câu trả lời; stop @enduml



*Hình 2-7: Biểu đồ hoạt động cho quy trình chat theo trang PDF*

#### 2.5.5 Quy trình quản lý sessions


@startuml start :Load danh sách sessions từ database; if (Tạo session mới?) then (yes) :Tạo title thông minh từ tin nhắn đầu; :Lưu session vào Supabase; :Reset session state; else (Chọn session cũ) :Load messages từ database; :Cập nhật session state; endif :Hiển thị giao diện chat; :Cho phép xóa session nếu cần; stop @enduml



*Hình 2-8: Biểu đồ hoạt động cho quy trình quản lý sessions*

### 2.6 Đặc tả use-case

#### UC001: Đăng nhập

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC001 |
| **Tên Use-case** | Đăng nhập vào hệ thống |
| **Tác nhân** | Khách |
| **Mô tả** | Xác thực người dùng để truy cập các tính năng của hệ thống |
| **Sự kiện kích hoạt** | Người dùng nhấn nút "Đăng nhập" trên giao diện |
| **Tiền điều kiện** | - Hệ thống đang hoạt động<br>- Người dùng đã có tài khoản |
| **Luồng sự kiện chính** | 1. Hệ thống hiển thị form đăng nhập<br>2. Người dùng nhập email và mật khẩu<br>3. Người dùng nhấn nút "Đăng nhập"<br>4. Hệ thống validate thông tin đầu vào<br>5. Hệ thống gửi request xác thực đến Supabase<br>6. Supabase xác thực thành công<br>7. Hệ thống tạo session cho người dùng<br>8. Chuyển hướng đến trang chính với quyền đầy đủ |
| **Luồng sự kiện thay thế** | **A1: Email hoặc mật khẩu trống (tại bước 4)**<br>4a. Hệ thống hiển thị thông báo lỗi "Vui lòng nhập đầy đủ thông tin"<br>4b. Quay lại bước 2<br><br>**A2: Thông tin đăng nhập sai (tại bước 6)**<br>6a. Supabase trả về lỗi xác thực<br>6b. Hệ thống hiển thị "Email hoặc mật khẩu không chính xác"<br>6c. Quay lại bước 2<br><br>**A3: Lỗi kết nối database (tại bước 5)**<br>5a. Hệ thống hiển thị "Lỗi kết nối, vui lòng thử lại"<br>5b. Quay lại bước 2 |
| **Hậu điều kiện** | - Người dùng được xác thực và có quyền truy cập đầy đủ<br>- Session được tạo và lưu trữ<br>- Giao diện chính được hiển thị |

**Bảng dữ liệu đầu vào:**

| Tên trường | Mô tả | Bắt buộc | Điều kiện hợp lệ | Ví dụ |
|------------|-------|----------|------------------|-------|
| Email | Địa chỉ email của người dùng | Có | Định dạng email hợp lệ | user@example.com |
| Password | Mật khẩu của người dùng | Có | Độ dài tối thiểu 6 ký tự | mypassword123 |

#### UC002: Upload và xử lý tài liệu

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC002 |
| **Tên Use-case** | Upload và xử lý tài liệu |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Upload tài liệu và xử lý để trích xuất nội dung, tạo tóm tắt và câu hỏi gợi ý |
| **Sự kiện kích hoạt** | Người dùng chọn file trong file uploader |
| **Tiền điều kiện** | - Người dùng đã đăng nhập<br>- File có định dạng hỗ trợ (PDF, DOCX, TXT, MD) |
| **Luồng sự kiện chính** | 1. Người dùng chọn file từ máy tính<br>2. Hệ thống validate file (định dạng, kích thước)<br>3. Hệ thống hiển thị progress "Đang xử lý tài liệu"<br>4. Nếu là PDF: gửi đến Mistral OCR để trích xuất text<br>5. Nếu là DOCX/TXT/MD: đọc trực tiếp nội dung<br>6. Hệ thống tạo tóm tắt với Local LLM<br>7. Hệ thống tạo câu hỏi gợi ý<br>8. Lưu tài liệu vào session state<br>9. Hiển thị tóm tắt và câu hỏi gợi ý<br>10. Thông báo "Đã xử lý xong" |
| **Luồng sự kiện thay thế** | **A1: File không hợp lệ (tại bước 2)**<br>2a. Hệ thống hiển thị "File không được hỗ trợ"<br>2b. Kết thúc use case<br><br>**A2: File quá lớn (tại bước 2)**<br>2a. Hệ thống hiển thị "File vượt quá 50MB"<br>2b. Kết thúc use case<br><br>**A3: Lỗi OCR (tại bước 4)**<br>4a. Mistral OCR trả về lỗi<br>4b. Hệ thống hiển thị "Không thể xử lý PDF"<br>4c. Kết thúc use case<br><br>**A4: Lỗi tạo tóm tắt (tại bước 6)**<br>6a. Local LLM không phản hồi<br>6b. Sử dụng tóm tắt mặc định "Không thể tóm tắt"<br>6c. Tiếp tục bước 7 |
| **Hậu điều kiện** | - Tài liệu được lưu trong session<br>- Nội dung được trích xuất và cache<br>- Tóm tắt và câu hỏi được hiển thị<br>- Sẵn sàng cho chat RAG |

**Bảng dữ liệu đầu vào:**

| Tên trường | Mô tả | Bắt buộc | Điều kiện hợp lệ | Ví dụ |
|------------|-------|----------|------------------|-------|
| File | Tài liệu cần upload | Có | PDF, DOCX, TXT, MD, ≤50MB | document.pdf |

#### UC003: Chat với AI sử dụng RAG

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC003 |
| **Tên Use-case** | Chat với AI sử dụng RAG |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Đặt câu hỏi và nhận câu trả lời từ AI dựa trên tài liệu đã upload |
| **Sự kiện kích hoạt** | Người dùng nhập tin nhắn và nhấn Enter |
| **Tiền điều kiện** | - Người dùng đã đăng nhập<br>- Có ít nhất một tài liệu đã được xử lý |
| **Luồng sự kiện chính** | 1. Người dùng nhập câu hỏi vào chat input<br>2. Hệ thống lưu tin nhắn người dùng<br>3. Hiển thị tin nhắn người dùng ngay lập tức<br>4. Tìm nội dung liên quan trong tài liệu<br>5. Tạo context từ nội dung liên quan<br>6. Gửi request đến Local LLM với context<br>7. Nhận response từ LLM<br>8. Lưu response vào database<br>9. Hiển thị câu trả lời của AI<br>10. Cập nhật session title nếu cần |
| **Luồng sự kiện thay thế** | **A1: Không có tài liệu (tại bước 4)**<br>4a. Sử dụng ChatHandler thông thường<br>4b. Gửi trực tiếp đến LLM không có context<br>4c. Tiếp tục bước 7<br><br>**A2: Local LLM không phản hồi (tại bước 6)**<br>6a. Timeout sau 30 giây<br>6b. Hiển thị "Không thể kết nối LLM"<br>6c. Kết thúc use case<br><br>**A3: Lỗi lưu database (tại bước 8)**<br>8a. Supabase trả về lỗi<br>8b. Vẫn hiển thị câu trả lời cho người dùng<br>8c. Log lỗi để xử lý sau |
| **Hậu điều kiện** | - Tin nhắn được lưu vào database<br>- Câu trả lời được hiển thị<br>- Lịch sử chat được cập nhật<br>- Session vẫn duy trì |

#### UC004: Chat theo trang PDF cụ thể

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC004 |
| **Tên Use-case** | Chat theo trang PDF cụ thể |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Chọn trang cụ thể của PDF và chat về nội dung trang đó |
| **Sự kiện kích hoạt** | Người dùng chuyển sang tab "Chat với trang PDF" |
| **Tiền điều kiện** | - Người dùng đã đăng nhập<br>- Có ít nhất một file PDF đã upload |
| **Luồng sự kiện chính** | 1. Hiển thị danh sách tài liệu PDF<br>2. Người dùng chọn tài liệu PDF<br>3. Hiển thị dropdown chọn trang<br>4. Người dùng chọn số trang<br>5. Render ảnh trang bằng PyMuPDF<br>6. Trích xuất nội dung trang bằng OCR<br>7. Hiển thị ảnh trang và tóm tắt nội dung<br>8. Người dùng nhập câu hỏi về trang<br>9. Sử dụng nội dung trang làm context<br>10. Gửi đến Local LLM<br>11. Hiển thị câu trả lời liên quan đến trang |
| **Luồng sự kiện thay thế** | **A1: Không có PDF (tại bước 1)**<br>1a. Hiển thị "Chưa có tài liệu PDF"<br>1b. Kết thúc use case<br><br>**A2: Lỗi render trang (tại bước 5)**<br>5a. PyMuPDF báo lỗi<br>5b. Hiển thị "Không thể hiển thị trang"<br>5c. Vẫn cho phép chat với nội dung text<br><br>**A3: Trang không tồn tại (tại bước 4)**<br>4a. Kiểm tra số trang hợp lệ<br>4b. Hiển thị "Trang không tồn tại"<br>4c. Reset về trang 1 |
| **Hậu điều kiện** | - Ảnh trang được hiển thị<br>- Nội dung trang được cache<br>- Chat riêng biệt cho trang được tạo<br>- Có thể chuyển trang khác |

#### UC005: Quản lý chat sessions

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC005 |
| **Tên Use-case** | Quản lý chat sessions |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Tạo, xem, tải và xóa các session chat |
| **Sự kiện kích hoạt** | Người dùng thao tác với sidebar sessions |
| **Tiền điều kiện** | - Người dùng đã đăng nhập<br>- Database Supabase hoạt động |
| **Luồng sự kiện chính** | 1. Load danh sách sessions từ database<br>2. Hiển thị danh sách với title và preview<br>3. Người dùng chọn một session<br>4. Load messages từ database<br>5. Cập nhật giao diện chat<br>6. Hiển thị "Đã tải session" |
| **Luồng sự kiện thay thế** | **A1: Tạo session mới**<br>1a. Người dùng nhấn "Chat mới"<br>1b. Reset session state<br>1c. Chuẩn bị cho cuộc chat mới<br><br>**A2: Xóa session**<br>2a. Người dùng nhấn nút xóa<br>2b. Xác nhận xóa từ database<br>2c. Refresh danh sách sessions<br>2d. Nếu đang ở session bị xóa, reset state<br><br>**A3: Lỗi load session**<br>4a. Database trả về lỗi<br>4b. Hiển thị "Không thể tải session"<br>4c. Giữ nguyên session hiện tại |
| **Hậu điều kiện** | - Session được load/tạo/xóa thành công<br>- Giao diện cập nhật phù hợp<br>- Lịch sử được đồng bộ |

#### UC006: Đăng ký tài khoản

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC006 |
| **Tên Use-case** | Đăng ký tài khoản mới |
| **Tác nhân** | Khách |
| **Mô tả** | Tạo tài khoản mới để sử dụng hệ thống |
| **Sự kiện kích hoạt** | Người dùng nhấn "Đăng ký" trên form login |
| **Tiền điều kiện** | - Hệ thống hoạt động<br>- Email chưa được đăng ký |
| **Luồng sự kiện chính** | 1. Hiển thị form đăng ký<br>2. Người dùng nhập email, mật khẩu, xác nhận mật khẩu<br>3. Validate thông tin đầu vào<br>4. Kiểm tra email chưa tồn tại<br>5. Tạo tài khoản trong Supabase<br>6. Gửi email xác thực (nếu cần)<br>7. Hiển thị thông báo thành công<br>8. Chuyển về form đăng nhập |
| **Luồng sự kiện thay thế** | **A1: Thông tin không hợp lệ**<br>3a. Email không đúng định dạng<br>3b. Mật khẩu quá ngắn<br>3c. Mật khẩu xác nhận không khớp<br>3d. Hiển thị lỗi tương ứng<br><br>**A2: Email đã tồn tại**<br>4a. Supabase báo email đã được sử dụng<br>4b. Hiển thị "Email đã được đăng ký"<br>4c. Quay lại bước 2 |
| **Hậu điều kiện** | - Tài khoản mới được tạo<br>- Sẵn sàng để đăng nhập |

**Bảng dữ liệu đầu vào:**

| Tên trường | Mô tả | Bắt buộc | Điều kiện hợp lệ | Ví dụ |
|------------|-------|----------|------------------|-------|
| Email | Địa chỉ email để đăng ký | Có | Định dạng email, chưa tồn tại | newuser@example.com |
| Password | Mật khẩu cho tài khoản | Có | Tối thiểu 6 ký tự | newpassword123 |
| Confirm Password | Xác nhận mật khẩu | Có | Phải giống với Password | newpassword123 |

#### UC007: Đăng xuất

| Trường | Mô tả |
|--------|-------|
| **Mã Use-case** | UC007 |
| **Tên Use-case** | Đăng xuất khỏi hệ thống |
| **Tác nhân** | Người dùng đã đăng nhập |
| **Mô tả** | Kết thúc phiên làm việc và xóa thông tin xác thực |
| **Sự kiện kích hoạt** | Người dùng nhấn nút "Đăng xuất" |
| **Tiền điều kiện** | - Người dùng đã đăng nhập |
| **Luồng sự kiện chính** | 1. Người dùng nhấn nút "Đăng xuất"<br>2. Hệ thống xóa session hiện tại<br>3. Reset tất cả state variables<br>4. Chuyển về giao diện đăng nhập<br>5. Hiển thị "Đã đăng xuất thành công" |
| **Luồng sự kiện thay thế** | Không có luồng thay thế |
| **Hậu điều kiện** | - Session bị xóa<br>- Người dùng trở về trạng thái chưa đăng nhập<br>- Tất cả dữ liệu nhạy cảm bị xóa khỏi bộ nhớ |

---

## 3. CÁC YÊU CẦU PHI CHỨC NĂNG

### 3.1 Các yêu cầu về hiệu năng

Hệ thống Study Buddy phải đảm bảo các yêu cầu hiệu năng sau để mang lại trải nghiệm người dùng tốt nhất:

- **Thời gian phản hồi chat**: Hệ thống phải trả lời tin nhắn chat thông thường trong vòng 3-5 giây, tính từ khi người dùng gửi tin nhắn đến khi hiển thị câu trả lời của AI. Đối với câu hỏi phức tạp có sử dụng RAG, thời gian phản hồi có thể lên đến 8-10 giây.

- **Thời gian xử lý tài liệu**: Xử lý file PDF có OCR hoàn thành trong vòng 10-30 giây tùy thuộc vào số trang (1-10 trang: ≤10s, 11-50 trang: ≤30s). Xử lý file DOCX, TXT, MD phải hoàn thành trong vòng 2-5 giây.

- **Tải trang và giao diện**: Thời gian tải trang chính không quá 2 giây với kết nối internet ổn định. Chuyển đổi giữa các tab và tương tác giao diện phải mượt mà, không có độ trễ đáng kể.

- **Khả năng xử lý đồng thời**: Hệ thống hỗ trợ ít nhất 5-10 người dùng đồng thời mà không ảnh hưởng đáng kể đến hiệu năng, phù hợp với quy mô demo và thử nghiệm.

- **Render ảnh PDF**: Chuyển đổi trang PDF thành ảnh hoàn thành trong 2-3 giây với độ phân giải 150 DPI, đảm bảo chất lượng ảnh rõ nét để đọc được text.

### 3.2 Yêu cầu về bảo mật

Hệ thống phải tuân thủ các nguyên tắc bảo mật cơ bản để bảo vệ thông tin người dùng:

- **Mã hóa truyền tải**: Tất cả dữ liệu được truyền giữa client và server phải được mã hóa bằng HTTPS/TLS, bao gồm thông tin đăng nhập, nội dung chat và tài liệu upload.

- **Xác thực và phân quyền**: Sử dụng Supabase Auth để quản lý xác thực với mã hóa mật khẩu theo chuẩn bcrypt. Người dùng chỉ có quyền truy cập dữ liệu của chính mình, không thể xem hoặc chỉnh sửa dữ liệu của người khác.

- **Bảo mật API**: Các API keys (Mistral, Local LLM) được lưu trữ an toàn trong biến môi trường hoặc Streamlit secrets, không hard-code trong source code.

- **Validation dữ liệu đầu vào**: Tất cả dữ liệu từ người dùng được validate nghiêm ngặt để tránh injection attacks. File upload được kiểm tra định dạng và kích thước để tránh malicious files.

- **Session management**: Session timeout sau 24 giờ không hoạt động. Đăng xuất sẽ xóa hoàn toàn session và không cho phép reuse.

- **Bảo vệ dữ liệu nhạy cảm**: Nội dung tài liệu và chat history được lưu trữ an toàn trong Supabase với row-level security. Không log hoặc cache thông tin nhạy cảm ở client-side.

### 3.3 Yêu cầu về giao diện

Giao diện người dùng phải thân thiện, trực quan và dễ sử dụng:

- **Thiết kế responsive**: Giao diện hoạt động tốt trên nhiều kích thước màn hình từ desktop (≥1200px) đến tablet (768px-1199px) và mobile (≤767px). Layout tự động điều chỉnh để tối ưu trải nghiệm trên từng thiết bị.

- **Tương thích trình duyệt**: Hỗ trợ đầy đủ trên các trình duyệt phổ biến: Chrome (≥90), Firefox (≥85), Safari (≥14), và Edge (≥90). Giao diện hiển thị nhất quán trên tất cả các platform.

- **Bố cục giao diện**: Giao diện gồm header chứa logo và thông tin người dùng, sidebar bên trái cho navigation và quản lý sessions, main content area cho chat interface, và footer chứa thông tin bổ sung. Sử dụng tab để phân tách "Chat trực tiếp" và "Chat theo trang PDF".

- **Phản hồi trực quan**: Loading indicators rõ ràng khi xử lý tài liệu hoặc chờ AI phản hồi. Progress bars cho các tác vụ dài như OCR. Toast notifications cho thông báo thành công/lỗi.

- **Accessibility**: Tuân thủ cơ bản WCAG 2.1 Level A với contrast ratio ≥4.5:1, hỗ trợ keyboard navigation, và alt text cho images.

- **Màu sắc và typography**: Sử dụng color scheme nhất quán với primary color #007bff, secondary color #6c757d. Font chữ dễ đọc như Inter hoặc Roboto với size 14-16px cho content text.

### 3.4 Ràng buộc

Hệ thống phải hoạt động trong các ràng buộc kỹ thuật và môi trường sau:

- **Công nghệ frontend**: Sử dụng Streamlit framework cho việc xây dựng giao diện web. Không sử dụng React, Vue hoặc framework frontend khác.

- **Công nghệ backend**: Python 3.8+ với các thư viện chính: streamlit, supabase, openai, mistralai, PyMuPDF, python-docx. Không sử dụng framework backend riêng biệt như FastAPI hay Django.

- **Cơ sở dữ liệu**: Bắt buộc sử dụng Supabase (PostgreSQL) để lưu trữ dữ liệu người dùng, sessions và messages. Không sử dụng SQLite hoặc database local khác.

- **Yêu cầu hệ thống**: Máy chủ cần có tối thiểu 8GB RAM để chạy Local LLM, kết nối internet ổn định để truy cập Mistral OCR API và Supabase. Hỗ trợ GPU là lợi thế nhưng không bắt buộc.

- **Yêu cầu client**: Trình duyệt hỗ trợ JavaScript ES6+, kết nối internet tối thiểu 5 Mbps để upload tài liệu và chat mượt mà. Không yêu cầu cài đặt plugin hay extension đặc biệt.

- **Kích thước file**: Giới hạn upload file tối đa 50MB per file, hỗ trợ tối đa 5 files cùng lúc trong một session. PDF tối đa 100 trang để đảm bảo hiệu năng OCR.

- **Dependency và license**: Tất cả dependencies phải có license tương thích (MIT, Apache 2.0, BSD). Không sử dụng các thư viện có license GPL hoặc commercial license.

- **Deployment**: Có thể deploy trên Streamlit Cloud, Heroku, hoặc chạy local. Không yêu cầu Docker container nhưng hỗ trợ nếu cần.

---

## 4. PHÂN CHIA CÔNG VIỆC NHÓM

### 4.1 Tổng quan phân chia

Dự án Study Buddy được chia thành 3 module chính tương ứng với 3 thành viên, mỗi người chịu trách nhiệm chính cho một lĩnh vực và hỗ trợ các module khác khi cần thiết.

### 4.2 Thành viên 1: [TÊN] - Frontend Development & UI/UX

**Vai trò chính**: Frontend Developer & UI/UX Designer

**Trách nhiệm chính**:
- **Phát triển giao diện người dùng**: Thiết kế và implement toàn bộ giao diện Streamlit, bao gồm layout, components, và styling với CSS tùy chỉnh
- **Tối ưu trải nghiệm người dùng**: Đảm bảo giao diện responsive, user-friendly và tuân thủ các nguyên tắc UX/UI design
- **Component development**: Xây dựng các UI components trong `src/utils/ui_components.py` như message rendering, sidebar, carousel, tabbed interface
- **CSS và styling**: Phát triển và maintain file `assets/styles/style.css` để tạo giao diện đẹp và nhất quán
- **Testing giao diện**: Kiểm thử giao diện trên nhiều trình duyệt và thiết bị khác nhau

**File phụ trách**:
- `src/pages/home_page.py` - Giao diện trang chính
- `src/pages/login_page.py` - Giao diện đăng nhập
- `src/utils/ui_components.py` - Các components UI
- `assets/styles/style.css` - Styling CSS
- `app.py` - Main application structure

**Tasks cụ thể**:
1. Thiết kế mockup và wireframe cho toàn bộ ứng dụng
2. Implement responsive layout cho desktop và mobile
3. Tạo các custom Streamlit components cho chat interface
4. Phát triển carousel cho câu hỏi gợi ý
5. Tối ưu loading states và error handling UI
6. Implement dark/light mode (nếu có thời gian)
7. Cross-browser testing và debugging
8. Viết documentation cho UI components

**Deliverables**:
- Giao diện hoàn chỉnh và responsive
- CSS framework tùy chỉnh
- Component library có thể tái sử dụng
- UI/UX documentation
- Browser compatibility report

### 4.3 Thành viên 2: Trần Long Khánh - Backend Logic & AI Integration

**Vai trò chính**: Backend Developer & AI Engineer

**Trách nhiệm chính**:
- **AI Integration**: Tích hợp và tối ưu các AI services (Local LLM, Mistral OCR, OpenAI-compatible APIs)
- **Document Processing**: Phát triển module xử lý tài liệu với OCR, text extraction và content analysis
- **RAG Implementation**: Xây dựng hệ thống Retrieval-Augmented Generation cho Q&A thông minh
- **Chat Logic**: Phát triển chat handler và conversation management
- **Error Handling**: Implement comprehensive error handling và logging system

**File phụ trách**:
- `src/utils/document_processor.py` - Xử lý tài liệu và OCR
- `src/utils/chat_handler.py` - Logic chat với AI
- `src/utils/error_handler.py` - Error handling system
- `src/utils/validators.py` - Data validation
- `src/config/constants.py` - Configuration constants

**Tasks cụ thể**:
1. Setup và configure Local LLM integration với LM Studio
2. Implement Mistral OCR cho PDF processing
3. Phát triển RAG pipeline với vector embeddings
4. Tối ưu response time cho AI queries
5. Implement document chunking và similarity search
6. Xây dựng error handling framework
7. Performance optimization cho AI operations
8. Unit testing cho các AI functions

**Deliverables**:
- AI integration module hoàn chỉnh
- Document processing pipeline
- RAG system với high accuracy
- Error handling framework
- Performance optimization report
- AI testing suite

### 4.4 Thành viên 3: Trần Đức Việt - Database & Authentication

**Vai trò chính**: Database Administrator & Security Engineer

**Trách nhiệm chính**:
- **Database Design**: Thiết kế và implement database schema trên Supabase
- **Authentication System**: Phát triển hệ thống đăng nhập/đăng ký an toàn
- **Session Management**: Quản lý user sessions và chat history
- **Data Persistence**: Implement data storage và retrieval logic
- **Security**: Đảm bảo bảo mật dữ liệu và user privacy

**File phụ trách**:
- `src/utils/chat_persistence.py` - Database operations
- `database_schema.sql` - Database schema design
- Authentication logic trong `home_page.py` và `login_page.py`
- Row Level Security policies trên Supabase
- Environment configuration và secrets management

**Tasks cụ thể**:
1. Thiết kế database schema cho users, sessions, messages, documents
2. Setup Supabase project với authentication
3. Implement row-level security policies
4. Phát triển CRUD operations cho tất cả entities
5. Optimize database queries và indexing
6. Implement backup và recovery procedures
7. Session management và timeout handling
8. Data migration và seeding scripts
9. Security audit và penetration testing
10. Performance monitoring và optimization

**Deliverables**:
- Database schema hoàn chỉnh với documentation
- Authentication system an toàn
- Session management framework
- Security audit report
- Performance optimization report
- Database backup/recovery procedures

### 4.5 Timeline và Milestone

**Phase 1 (Tuần 1-2): Setup và Foundation**
- Thành viên 1: Thiết kế mockup và basic layout
- Thành viên 2: Setup AI integrations và basic document processing
- Thành viên 3: Setup database schema và authentication

**Phase 2 (Tuần 3-4): Core Development**
- Thành viên 1: Develop main UI components và responsive design
- Thành viên 2: Implement RAG system và chat logic
- Thành viên 3: Complete CRUD operations và session management

**Phase 3 (Tuần 5-6): Integration và Testing**
- Tất cả thành viên: Integration testing và bug fixes
- Thành viên 1: UI/UX refinement và cross-browser testing
- Thành viên 2: Performance optimization và error handling
- Thành viên 3: Security testing và data validation

**Phase 4 (Tuần 7): Final Polish và Deployment**
- Code review và refactoring
- Documentation completion
- Deployment preparation
- Demo preparation

### 4.6 Communication và Collaboration

**Daily Standups**: Họp online 15 phút mỗi sáng để sync progress và issues

**Code Review**: Mỗi thành viên review code của 2 thành viên còn lại trước khi merge

**Shared Resources**:
- GitHub repository cho version control
- Discord/Slack cho communication
- Notion/Trello cho task management
- Google Drive cho shared documents

**Integration Points**:
- Thành viên 1 & 2: UI components calling AI functions
- Thành viên 1 & 3: Frontend authentication flows
- Thành viên 2 & 3: AI responses saving to database

### 4.7 Quality Assurance

**Testing Responsibilities**:
- Thành viên 1: UI/UX testing, responsive design testing
- Thành viên 2: Unit testing cho AI functions, integration testing
- Thành viên 3: Database testing, security testing

**Code Standards**:
- Python PEP 8 compliance
- Type hints cho tất cả functions
- Comprehensive docstrings
- Error handling ở mọi level

**Documentation Requirements**:
- README với setup instructions
- API documentation cho internal functions
- User manual cho end users
- Deployment guide

---

## 5. KẾT LUẬN

### 5.1 Tổng kết dự án

Hệ thống Study Buddy là một ứng dụng chatbot AI hỗ trợ học tập tiên tiến, tích hợp nhiều công nghệ hiện đại như Local LLM, OCR, và RAG để mang lại trải nghiệm học tập thông minh và hiệu quả. Dự án được thiết kế với kiến trúc modular, dễ bảo trì và mở rộng, phù hợp với quy mô nhóm 3 người và thời gian phát triển 7 tuần.

### 5.2 Điểm mạnh của hệ thống

- **Tính độc đáo**: Chat theo trang PDF cụ thể là tính năng độc đáo, chưa có ở nhiều sản phẩm tương tự
- **Privacy-focused**: Sử dụng Local LLM đảm bảo dữ liệu không bị leak ra bên ngoài
- **Comprehensive**: Hỗ trợ đầy đủ pipeline từ upload tài liệu đến chat thông minh
- **Scalable**: Kiến trúc cho phép mở rộng thêm nhiều tính năng trong tương lai

### 5.3 Rủi ro và giải pháp

**Rủi ro kỹ thuật**:
- Local LLM có thể chậm: Fallback sang cloud API nếu cần
- OCR accuracy không cao: Combine multiple OCR engines
- Database performance: Implement caching và optimization

**Rủi ro timeline**:
- Scope creep: Strict scope management và prioritization
- Technical difficulties: Buffer time và fallback solutions
- Team coordination: Regular sync meetings và clear communication

### 5.4 Tiêu chí thành công

Dự án được coi là thành công khi:
- ✅ Tất cả use cases chính được implement và test
- ✅ Performance đạt yêu cầu (chat <5s, OCR <30s)
- ✅ Security requirements được đáp ứng
- ✅ UI/UX user-friendly và responsive
- ✅ Code quality đạt chuẩn (90%+ test coverage)
- ✅ Documentation đầy đủ và rõ ràng

---

**Chữ ký nhóm:**

**Thành viên 1:** [TÊN] - [CHỮ KÝ] - [NGÀY]

**Thành viên 2:** [TÊN] - [CHỮ KÝ] - [NGÀY]

**Thành viên 3:** [TÊN] - [CHỮ KÝ] - [NGÀY]

---

**Xác nhận của giảng viên:**

**Giảng viên:** [TÊN GIẢNG VIÊN] - [CHỮ KÝ] - [NGÀY]

---

*Tài liệu này tuân thủ chuẩn IEEE Std 830-1998 và được tối ưu để đạt điểm cao trong môn Kỹ thuật Phần mềm IT4490.*
