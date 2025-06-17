import streamlit as st
from supabase import create_client
import bcrypt
from ..utils.validators import UserValidator
from ..utils.error_handler import (
    handle_error, safe_database_operation, show_success_message, 
    show_error_message, error_boundary, DatabaseError, ValidationError
)

# --- Kết nối Supabase ---
SUPABASE_URL = "https://skbclvpercuqtyevuxqr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrYmNsdnBlcmN1cXR5ZXZ1eHFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4NzMwNDIsImV4cCI6MjA2NTQ0OTA0Mn0.DTBbMCVSHZKjXkEzLDjmbYgYGR42NEYozcr3BvNN7x0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@error_boundary("Database connection", show_user=True)
def get_supabase_client():
    """Lấy Supabase client với error handling"""
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        raise DatabaseError("Không thể kết nối database", "db_connection_failed")

@error_boundary("User authentication", show_user=True)
def authenticate_user(username: str, password: str):
    """Xác thực user với validation và error handling"""
    # Validate inputs
    is_valid_username, username_error = UserValidator.validate_username(username)
    if not is_valid_username:
        raise ValidationError(username_error, "invalid_username")
    
    is_valid_password, password_error = UserValidator.validate_password(password)
    if not is_valid_password:
        raise ValidationError(password_error, "invalid_password")
    
    # Database operation
    def db_operation():
        result = supabase.table("user").select("*").eq("username", username.strip()).execute()
        return result
    
    result = safe_database_operation(db_operation)
    
    if result and result.data:
        user = result.data[0]
        if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return True, user, None
        else:
            return False, None, "Sai mật khẩu"
    else:
        return False, None, "Không tìm thấy người dùng"

@error_boundary("User registration", show_user=True)
def register_user(username: str, email: str, password: str, confirm_password: str):
    """Đăng ký user mới với validation"""
    # Validate all inputs
    validation_results = {
        'username': UserValidator.validate_username(username),
        'email': UserValidator.validate_email(email),
        'password': UserValidator.validate_password(password)
    }
    
    # Check validation results
    for field, (is_valid, error_msg) in validation_results.items():
        if not is_valid:
            raise ValidationError(f"{field.title()}: {error_msg}", f"invalid_{field}")
    
    # Check password confirmation
    if password != confirm_password:
        raise ValidationError("Mật khẩu xác nhận không khớp", "password_mismatch")
    
    # Check if email exists
    def check_email_exists():
        return supabase.table("user").select("*").eq("email", email.strip()).execute()
    
    existing_user = safe_database_operation(check_email_exists)
    if existing_user and existing_user.data:
        raise ValidationError("Email đã được sử dụng", "email_exists")
    
    # Check if username exists
    def check_username_exists():
        return supabase.table("user").select("*").eq("username", username.strip()).execute()
    
    existing_username = safe_database_operation(check_username_exists)
    if existing_username and existing_username.data:
        raise ValidationError("Username đã được sử dụng", "username_exists")
    
    # Create new user
    def create_user():
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return supabase.table("user").insert({
            "username": username.strip(),
            "email": email.strip(),
            "password_hash": hashed_password
        }).execute()
    
    result = safe_database_operation(create_user)
    return result is not None

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
        with st.form("login_form"):
            username = st.text_input("Tên người dùng", placeholder="Nhập username (3-20 ký tự)")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            submit_login = st.form_submit_button("🔐 Đăng nhập", use_container_width=True)
            
            if submit_login:
                if not username or not password:
                    show_error_message('authentication_required')
                    return
                
                try:
                    success, user, error_msg = authenticate_user(username, password)
                    if success:
                        show_success_message('login_success')
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["id"]
                        st.rerun()
                    else:
                        st.error(f"❌ {error_msg}")
                except (ValidationError, DatabaseError) as e:
                    # Error đã được handle trong decorator
                    pass
                except Exception as e:
                    handle_error(e, "Login process", show_user=True)

    with tab2:
        st.markdown("### Tạo tài khoản mới")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input(
                    "Tên người dùng *", 
                    placeholder="3-20 ký tự, chữ cái và số",
                    help="Username chỉ được chứa chữ cái, số và dấu gạch dưới"
                )
                email_reg = st.text_input(
                    "Email *", 
                    placeholder="example@email.com",
                    help="Email hợp lệ để xác nhận tài khoản"
                )
            
            with col2:
                password_reg = st.text_input(
                    "Mật khẩu *", 
                    type="password",
                    placeholder="Ít nhất 6 ký tự",
                    help="Mật khẩu mạnh để bảo vệ tài khoản"
                )
                confirm_password = st.text_input(
                    "Xác nhận mật khẩu *", 
                    type="password",
                    placeholder="Nhập lại mật khẩu",
                    help="Phải trùng khớp với mật khẩu ở trên"
                )
            
            # Real-time validation feedback
            if username:
                is_valid_username, username_error = UserValidator.validate_username(username)
                if not is_valid_username:
                    st.error(f"❌ Username: {username_error}")
                else:
                    st.success("✅ Username hợp lệ")
            
            if email_reg:
                is_valid_email, email_error = UserValidator.validate_email(email_reg)
                if not is_valid_email:
                    st.error(f"❌ Email: {email_error}")
                else:
                    st.success("✅ Email hợp lệ")
            
            if password_reg:
                is_valid_password, password_error = UserValidator.validate_password(password_reg)
                if not is_valid_password:
                    st.error(f"❌ Mật khẩu: {password_error}")
                else:
                    st.success("✅ Mật khẩu hợp lệ")
            
            if password_reg and confirm_password:
                if password_reg != confirm_password:
                    st.error("❌ Mật khẩu xác nhận không khớp")
                else:
                    st.success("✅ Mật khẩu xác nhận khớp")
            
            st.markdown("---")
            submit_register = st.form_submit_button("✨ Tạo tài khoản", use_container_width=True)
            
            if submit_register:
                if not all([username, email_reg, password_reg, confirm_password]):
                    st.error("❌ Vui lòng điền đầy đủ tất cả thông tin bắt buộc (*)")
                    return
                
                try:
                    success = register_user(username, email_reg, password_reg, confirm_password)
                    if success:
                        show_success_message('account_created')
                        st.info("👆 Bây giờ bạn có thể đăng nhập bằng tài khoản vừa tạo!")
                        st.balloons()  # Celebration effect
                except (ValidationError, DatabaseError) as e:
                    # Error đã được handle trong decorator
                    pass
                except Exception as e:
                    handle_error(e, "Registration process", show_user=True)
