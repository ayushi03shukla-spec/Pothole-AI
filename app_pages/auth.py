import streamlit as st
import requests
from datetime import datetime
import re


BACKEND_URL = "http://127.0.0.1:5000"


def validate_email(email):
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    return True, "Password is strong"


def get_error_message(response):
    """Extract a useful error message from a backend response."""
    try:
        data = response.json()
        return data.get("error") or data.get("msg") or str(data)
    except ValueError:
        return response.text or f"HTTP {response.status_code}"


def show_login():
    """Display login page and authenticate through Flask backend."""

    st.markdown("# 🔐 Login to Pothole AI")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Sign In")

        email = st.text_input(
            "📧 Email Address",
            placeholder="you@example.com",
            key="login_email",
        )
        email = email.strip().lower()

        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )

        if st.button(
            "🚀 Login",
            use_container_width=True,
            key="backend_login",
        ):
            if not email or not password:
                st.error("❌ Please fill all fields")

            elif not validate_email(email):
                st.error("❌ Invalid email format")

            else:
                try:
                    with st.spinner("Signing in..."):
                        response = requests.post(
                            f"{BACKEND_URL}/api/auth/login",
                            json={
                                "email": email,
                                "password": password,
                            },
                            timeout=30,
                        )

                    if response.ok:
                        data = response.json()
                        token = data.get("token")

                        if not token:
                            st.error(
                                "Backend login succeeded but no JWT token was returned."
                            )
                            return

                        st.session_state.authenticated = True
                        st.session_state.token = token

                        st.session_state.user = {
                            "name": email.split("@")[0],
                            "email": email,
                            "role": "user",
                            "login_time": datetime.now(),
                        }

                        st.success("✅ Login successful!")
                        st.rerun()

                    else:
                        st.error(
                            f"❌ Login failed: {get_error_message(response)}"
                        )

                except requests.RequestException as exc:
                    st.error(
                        "❌ Could not connect to Flask backend. "
                        "Make sure the backend is running on port 5000."
                    )
                    st.caption(str(exc))

        st.markdown("---")
        st.info(
            "Use an account created through the Pothole AI backend "
            "registration."
        )


def show_register():
    """Display registration page and create account through Flask backend."""

    st.markdown("# 📝 Create Account")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Sign Up")

        name = st.text_input(
            "👤 Full Name",
            placeholder="John Doe",
            key="register_name",
        )

        email = st.text_input(
            "📧 Email Address",
            placeholder="you@example.com",
            key="register_email",
        )

        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="••••••••",
            key="register_password",
        )
        email = email.strip().lower()

        confirm_password = st.text_input(
            "🔑 Confirm Password",
            type="password",
            placeholder="••••••••",
            key="register_confirm_password",
        )

        agree_terms = st.checkbox(
            "I agree to Terms & Conditions",
            key="register_terms",
        )

        if st.button(
            "✨ Create Account",
            use_container_width=True,
            key="backend_register",
        ):
            if not all(
                [name, email, password, confirm_password]
            ):
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
                    try:
                        with st.spinner("Creating your account..."):
                            response = requests.post(
                                f"{BACKEND_URL}/api/auth/register",
                                json={
                                    "name": name,
                                    "email": email,
                                    "password": password,
                                },
                                timeout=30,
                            )

                        if response.ok:
                            data = response.json()

                            st.success(
                                data.get(
                                    "message",
                                    "✅ Registration successful!",
                                )
                            )

                            st.info(
                                "Your account has been created. "
                                "Go to Login and sign in."
                            )

                        else:
                            st.error(
                                f"❌ Registration failed: "
                                f"{get_error_message(response)}"
                            )

                    except requests.RequestException as exc:
                        st.error(
                            "❌ Could not connect to Flask backend. "
                            "Make sure the backend is running on port 5000."
                        )
                        st.caption(str(exc))

        st.markdown("---")

        st.markdown(
            """
            **Password Requirements:**
            - Minimum 8 characters
            - At least one uppercase letter
            - At least one number
            """
        )
