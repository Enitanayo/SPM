import streamlit as st

def show_login_page(auth):
    """Login page UI"""
    # Simple centered header
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0 2rem 0;'>
        <h1 style='font-size: 2.8rem; margin-bottom: 0.5rem; color: #1e293b;'>🔍 Campus Lost & Found</h1>
        <p style='color: #64748b; font-size: 1.1rem; font-weight: 400;'>Connect items with their owners</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # Add a container with purple background
        st.markdown('<div class="login-form-card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if username and password:
                    success, message, user = auth.login_user(username, password)
                    if success:
                        st.session_state.user = user
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email (optional)")
            register_btn = st.form_submit_button("Register")
            
            if register_btn:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        # Force role to be 'student' for public registration
                        success, message = auth.register_user(new_username, new_password, 'student', email)
                        if success:
                            st.success(message)
                            # Auto-login after successful registration
                            login_success, login_message, user = auth.login_user(new_username, new_password)
                            if login_success:
                                st.session_state.user = user
                                st.session_state.page = "dashboard"
                                st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Please fill all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close login-form-card