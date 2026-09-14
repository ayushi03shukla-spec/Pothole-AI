import streamlit as st
import hashlib
import mysql.connector
from datetime import datetime
import re

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pothole_ai"
        )
        return connection
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def show_login():
    """Display login page"""
    st.markdown("# 🔐 Login to Pothole AI")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign In")
        
        email = st.text_input("📧 Email Address", placeholder="you@example.com")
        password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
        
        col_login, col_demo = st.columns(2)
        
        with col_login:
            if st.button("🚀 Login", use_container_width=True):
                if not email or not password:
                    st.error("❌ Please fill all fields")
                elif not validate_email(email):
                    st.error("❌ Invalid email format")
                else:
                    # Demo authentication
                    if email == "anamika@psit.ac.in" and password == "Anamika@123":
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            "name": "Anamika",
                            "email": email,
                            "role": "frontend_lead",
                            "login_time": datetime.now()
                        }
                        st.success("✅ Login successful!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
        
        with col_demo:
            if st.button("👤 Demo Login", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user = {
                    "name": "Demo User",
                    "email": "demo@pothole.ai",
                    "role": "user",
                    "login_time": datetime.now()
                }
                st.success("✅ Demo login successful!")
                st.balloons()
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        **Demo Credentials:**
        - Email: `anamika@psit.ac.in`
        - Password: `Anamika@123`
        
        Or click "Demo Login" to try the system
        """)

def show_register():
    """Display registration page"""
    st.markdown("# 📝 Create Account")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign Up")
        
        name = st.text_input("👤 Full Name", placeholder="John Doe")
        email = st.text_input("📧 Email Address", placeholder="you@example.com")
        password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
        confirm_password = st.text_input("🔑 Confirm Password", type="password", placeholder="••••••••")
        agree_terms = st.checkbox("I agree to Terms & Conditions")
        
        if st.button("✨ Create Account", use_container_width=True):
            # Validation
            if not all([name, email, password, confirm_password]):
                st.error("❌ Please fill all fields")
            elif not validate_email(email):
                st.error("❌ Invalid email format")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif not agree_terms:
                st.error("❌ You must agree to terms & conditions")
            else:
                is_valid, message = validate_password(password)
                if not is_valid:
                    st.error(f"❌ {message}")
                else:
                    # Demo registration success
                    st.success("✅ Registration successful! Please login.")
                    st.info("""
                    Your account has been created!
                    
                    **Your Details:**
                    - Name: {name}
                    - Email: {email}
                    
                    Please login with your credentials.
                    """.format(name=name, email=email))
        
        st.markdown("---")
        st.markdown("""
        **Password Requirements:**
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one number
        """)
