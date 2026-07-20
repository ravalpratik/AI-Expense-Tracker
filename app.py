"""
AI Expense Tracker – Main Application Entry Point
BCA 5th Semester AI Major Project
"""

import streamlit as st
from streamlit_option_menu import option_menu
from database import init_db
from auth import AuthManager
from utils import init_session_defaults, apply_custom_css

# Page render functions
from pages import dashboard, add_expense, ocr_scanner, predictions, analytics, profile

st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_session_defaults()
apply_custom_css(st.session_state.get("dark_mode", True))


def render_login_page():
    """Render login and registration forms."""
    st.markdown('<div class="brand-title">💰 AI Expense Tracker</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#94a3b8;margin-bottom:2rem;">'
        "Smart expense management with OCR & ML predictions</p>",
        unsafe_allow_html=True,
    )

    auth = AuthManager()
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    success, msg = auth.login(username, password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab2:
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username", key="reg_user")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
            if submitted:
                error = auth.validate_registration(username, email, password, confirm)
                if error:
                    st.error(error)
                else:
                    success, msg = auth.register(username, email, password, full_name)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)


def render_sidebar():
    """Render sidebar navigation and theme toggle."""
    with st.sidebar:
        st.markdown(
            f"### 👋 {st.session_state.get('full_name', 'User')}",
            unsafe_allow_html=True,
        )
        st.caption(st.session_state.get("email", ""))

        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get("dark_mode", True))
        st.session_state["dark_mode"] = dark_mode
        apply_custom_css(dark_mode)

        st.divider()

        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "Add Expense", "OCR Scanner", "Predictions", "Analytics", "Profile"],
            icons=["speedometer2", "plus-circle", "camera", "graph-up-arrow", "bar-chart", "person"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "4px 0",
                    "border-radius": "8px",
                },
                "nav-link-selected": {"background-color": "#6366f1"},
            },
        )

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            AuthManager.logout()
            st.rerun()

        return selected


PAGE_RENDERERS = {
    "Dashboard": dashboard.render,
    "Add Expense": add_expense.render,
    "OCR Scanner": ocr_scanner.render,
    "Predictions": predictions.render,
    "Analytics": analytics.render,
    "Profile": profile.render,
}


def main():
    """Main application router."""
    if not AuthManager.is_authenticated():
        render_login_page()
        return

    page = render_sidebar()
    renderer = PAGE_RENDERERS.get(page, dashboard.render)
    renderer()


if __name__ == "__main__":
    main()
