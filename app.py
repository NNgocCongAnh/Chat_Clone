import streamlit as st
from src.pages import login_page
from src.pages import home_page

# Khởi tạo biến session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Điều hướng
if st.session_state.authenticated:
    home_page.main()
else:
    login_page.main()
