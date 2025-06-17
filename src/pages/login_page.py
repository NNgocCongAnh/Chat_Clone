import streamlit as st
from supabase import create_client
import bcrypt

# --- Kết nối Supabase ---
SUPABASE_URL = "https://skbclvpercuqtyevuxqr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrYmNsdnBlcmN1cXR5ZXZ1eHFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4NzMwNDIsImV4cCI6MjA2NTQ0OTA0Mn0.DTBbMCVSHZKjXkEzLDjmbYgYGR42NEYozcr3BvNN7x0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # --- Header với Study Buddy ---
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #007bff; font-size: 3rem; margin-bottom: 0.5rem;">
            💬 Study Buddy
        </h1>
        <p style="color: #6c757d; font-size: 1.2rem; margin-bottom: 2rem;">
            AI Learning Assistant - Trợ lý học tập thông minh
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Giao diện login ---
    st.title("🔐 Đăng nhập / Đăng ký")

    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

    with tab1:
        username = st.text_input("Tên người dùng", key="signin_username")
        password = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            res = supabase.table("user").select("*").eq("username", username).execute()
            if res.data:
                user = res.data[0]
                if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
                    st.success("Đăng nhập thành công!")
                    st.session_state.authenticated = True
                    st.session_state.user_id = user["id"]
                    st.rerun()
                else:
                    st.error("Sai mật khẩu.")
            else:
                st.error("Không tìm thấy người dùng. Vui lòng đăng ký")

    with tab2:
        username = st.text_input("Tên người dùng", key="register_username")
        email_reg = st.text_input("Email", key="register_email")
        password_reg = st.text_input("Mật khẩu", type="password", key="register_pass")
        confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="register_confirm_pass")
        if password_reg != confirm_password:
            st.error("Mật khẩu không khớp!")
        elif len(password_reg) < 6:
            st.error("Mật khẩu phải có ít nhất 6 ký tự!")
        elif not email_reg or not username or not password_reg:
            st.error("Vui lòng điền đầy đủ thông tin!")
        elif email_reg and username and password_reg and password_reg == confirm_password:
            # Kiểm tra xem email đã tồn tại chưa
            res = supabase.table("user").select("*").eq("email", email_reg).execute()
            if res.data:
                st.error("Email đã được sử dụng. Vui lòng chọn email khác.")
                st.stop()

            # Tạo tài khoản mới
            if not username.isalnum():
                st.error("Tên người dùng chỉ được chứa chữ cái và số.")
                st.stop()
        if st.button("Tạo tài khoản"):
            hashed = bcrypt.hashpw(password_reg.encode(), bcrypt.gensalt()).decode()
            try:
                supabase.table("user").insert({
                    "username": username,
                    "email": email_reg,
                    "password_hash": hashed
                }).execute()
                st.success("Tạo tài khoản thành công! Đăng nhập nhé.")
            except Exception as e:
                st.error(f"Có lỗi xảy ra khi tạo tài khoản: {e}")
                # st.error("Email đã tồn tại hoặc có lỗi.")
