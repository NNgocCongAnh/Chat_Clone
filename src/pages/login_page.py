import streamlit as st
from supabase import create_client
import bcrypt
from ..utils.validators import UserValidator

# Enhanced Login Page Implementation - v2.0
# Author: Nguyễn Ngọc Công Anh - Frontend & UI/UX Enhancement
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

def add_login_css():
    """Enhanced CSS cho login page với modern animations"""
    st.markdown("""
    <style>
    /* Enhanced login page styling */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    
    /* Animated background */
    .login-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        z-index: -1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Enhanced login container */
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 2rem auto;
        animation: slideInUp 0.8s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced hero section */
    .login-hero {
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-hero h1 {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: pulse 2s ease-in-out infinite alternate;
    }
    
    @keyframes pulse {
        from { opacity: 0.8; }
        to { opacity: 1; }
    }
    
    .login-hero p {
        font-size: 1.3rem;
        color: #6b7280;
        margin-bottom: 2rem;
        opacity: 0;
        animation: fadeIn 1s ease-out 0.5s forwards;
    }
    
    @keyframes fadeIn {
        to { opacity: 1; }
    }
    
    /* Enhanced form styling */
    .stTextInput > div > div > input {
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        background: rgba(248, 250, 252, 0.8);
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
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
        transition: left 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(248, 250, 252, 0.8);
        backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 16px;
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        color: #6b7280;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    /* Floating elements animation */
    .floating-elements {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .floating-element {
        position: absolute;
        width: 20px;
        height: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 20s infinite linear;
    }
    
    @keyframes float {
        from {
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        to {
            transform: translateY(-100px) rotate(360deg);
            opacity: 0;
        }
    }
    
    /* Success and error message enhancements */
    .stSuccess {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border: none;
        border-radius: 12px;
        animation: slideInRight 0.5s ease-out;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        border: none;
        border-radius: 12px;
        animation: shake 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Form validation indicators */
    .validation-success {
        color: #10b981;
        animation: bounceIn 0.5s ease-out;
    }
    
    .validation-error {
        color: #ef4444;
        animation: shake 0.5s ease-out;
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_animated_background():
    """Render animated background elements"""
    st.markdown("""
    <div class="login-background"></div>
    <div class="floating-elements">
        <div class="floating-element" style="left: 10%; animation-delay: 0s;"></div>
        <div class="floating-element" style="left: 20%; animation-delay: 2s;"></div>
        <div class="floating-element" style="left: 30%; animation-delay: 4s;"></div>
        <div class="floating-element" style="left: 40%; animation-delay: 6s;"></div>
        <div class="floating-element" style="left: 50%; animation-delay: 8s;"></div>
        <div class="floating-element" style="left: 60%; animation-delay: 10s;"></div>
        <div class="floating-element" style="left: 70%; animation-delay: 12s;"></div>
        <div class="floating-element" style="left: 80%; animation-delay: 14s;"></div>
        <div class="floating-element" style="left: 90%; animation-delay: 16s;"></div>
    </div>
    """, unsafe_allow_html=True)

def render_enhanced_hero():
    """Render enhanced hero section"""
    st.markdown("""
    <div class="login-hero">
        <h1>🎓 Study Buddy</h1>
        <p>✨ AI Learning Assistant - Trợ lý học tập thông minh ✨</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                <small style="color: #6b7280;">AI-Powered</small>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                <small style="color: #6b7280;">Smart Learning</small>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                <small style="color: #6b7280;">Interactive Chat</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Enhanced page setup
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # Add enhanced CSS
    add_login_css()
    
    # Render animated background
    render_animated_background()
    
    # Main container with glassmorphism
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Enhanced hero section
    render_enhanced_hero()
    
    # Enhanced title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        ">🔐 Đăng nhập / Đăng ký</h2>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced tabs
    tab1, tab2 = st.tabs(["🔑 Đăng nhập", "✨ Đăng ký"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Tên người dùng", placeholder="Nhập username (3-20 ký tự)")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            submit_login = st.form_submit_button("🔐 Đăng nhập", use_container_width=True)
            
            if submit_login:
                if not username or not password:
                    st.markdown('<div class="validation-error">❌ Vui lòng nhập đầy đủ thông tin đăng nhập</div>', 
                               unsafe_allow_html=True)
                    return
                
                # Enhanced loading animation
                with st.spinner("🔍 Đang xác thực..."):
                    try:
                        success, user, error_msg = authenticate_user(username, password)
                        if success:
                            st.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #10b981, #059669);
                                color: white;
                                padding: 1rem;
                                border-radius: 12px;
                                text-align: center;
                                margin: 1rem 0;
                                animation: slideInRight 0.5s ease-out;
                            ">
                                ✅ Đăng nhập thành công! Chào mừng bạn quay lại! 🎉
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.session_state.authenticated = True
                            st.session_state.user_id = user["id"]
                            
                            # Celebration effect
                            st.balloons()
                            
                            # Delay để user thấy success message
                            import time
                            time.sleep(1)
                            
                            st.rerun()
                        else:
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #ef4444, #dc2626);
                                color: white;
                                padding: 1rem;
                                border-radius: 12px;
                                text-align: center;
                                margin: 1rem 0;
                                animation: shake 0.5s ease-out;
                            ">
                                ❌ {error_msg}
                            </div>
                            """, unsafe_allow_html=True)
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
            
            # Enhanced real-time validation feedback
            if username:
                is_valid_username, username_error = UserValidator.validate_username(username)
                if not is_valid_username:
                    st.markdown(f'<div class="validation-error">❌ Username: {username_error}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown('<div class="validation-success">✅ Username hợp lệ</div>', 
                               unsafe_allow_html=True)
            
            if email_reg:
                is_valid_email, email_error = UserValidator.validate_email(email_reg)
                if not is_valid_email:
                    st.markdown(f'<div class="validation-error">❌ Email: {email_error}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown('<div class="validation-success">✅ Email hợp lệ</div>', 
                               unsafe_allow_html=True)
            
            if password_reg:
                is_valid_password, password_error = UserValidator.validate_password(password_reg)
                if not is_valid_password:
                    st.markdown(f'<div class="validation-error">❌ Mật khẩu: {password_error}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown('<div class="validation-success">✅ Mật khẩu hợp lệ</div>', 
                               unsafe_allow_html=True)
            
            if password_reg and confirm_password:
                if password_reg != confirm_password:
                    st.markdown('<div class="validation-error">❌ Mật khẩu xác nhận không khớp</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown('<div class="validation-success">✅ Mật khẩu xác nhận khớp</div>', 
                               unsafe_allow_html=True)
            
            st.markdown("---")
            submit_register = st.form_submit_button("✨ Tạo tài khoản", use_container_width=True)
            
            if submit_register:
                if not all([username, email_reg, password_reg, confirm_password]):
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #ef4444, #dc2626);
                        color: white;
                        padding: 1rem;
                        border-radius: 12px;
                        text-align: center;
                        margin: 1rem 0;
                        animation: shake 0.5s ease-out;
                    ">
                        ❌ Vui lòng điền đầy đủ tất cả thông tin bắt buộc (*)
                    </div>
                    """, unsafe_allow_html=True)
                    return
                
                # Enhanced loading for registration
                with st.spinner("✨ Đang tạo tài khoản..."):
                    try:
                        success = register_user(username, email_reg, password_reg, confirm_password)
                        if success:
                            st.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #10b981, #059669);
                                color: white;
                                padding: 2rem;
                                border-radius: 16px;
                                text-align: center;
                                margin: 1rem 0;
                                animation: slideInRight 0.5s ease-out;
                            ">
                                <h3 style="margin: 0 0 1rem 0; color: white;">🎉 Tài khoản đã được tạo thành công!</h3>
                                <p style="margin: 0; color: rgba(255,255,255,0.9);">
                                    👆 Bây giờ bạn có thể đăng nhập bằng tài khoản vừa tạo!
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Enhanced celebration effect
                            st.balloons()
                            st.snow()  # Additional effect
                            
                    except (ValidationError, DatabaseError) as e:
                        # Error đã được handle trong decorator
                        pass
                    except Exception as e:
                        handle_error(e, "Registration process", show_user=True)
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
