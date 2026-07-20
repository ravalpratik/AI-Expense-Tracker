"""
Authentication module – registration, login, logout with bcrypt hashing.
"""

import re
import bcrypt
import streamlit as st
from sqlalchemy.exc import IntegrityError
from database import get_session, User


class AuthManager:
    """Handles user authentication and session management."""

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify plain password against stored hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def validate_registration(username: str, email: str, password: str, confirm: str) -> str | None:
        """Return error message or None if valid."""
        if not username or len(username) < 3:
            return "Username must be at least 3 characters."
        if not AuthManager.EMAIL_PATTERN.match(email):
            return "Invalid email address."
        if len(password) < 6:
            return "Password must be at least 6 characters."
        if password != confirm:
            return "Passwords do not match."
        return None

    def register(self, username: str, email: str, password: str, full_name: str = "") -> tuple[bool, str]:
        """Register a new user. Returns (success, message)."""
        session = get_session()
        try:
            user = User(
                username=username.strip(),
                email=email.strip().lower(),
                password_hash=self.hash_password(password),
                full_name=full_name.strip() or username.strip(),
            )
            session.add(user)
            session.commit()
            return True, "Registration successful! Please login."
        except IntegrityError:
            session.rollback()
            return False, "Username or email already exists."
        except Exception as exc:
            session.rollback()
            return False, f"Registration failed: {exc}"
        finally:
            session.close()

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate user. Returns (success, message)."""
        session = get_session()
        try:
            user = session.query(User).filter(
                (User.username == username.strip()) | (User.email == username.strip().lower())
            ).first()
            if not user:
                return False, "Invalid username or password."
            if not self.verify_password(password, user.password_hash):
                return False, "Invalid username or password."
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user.id
            st.session_state["username"] = user.username
            st.session_state["full_name"] = user.full_name
            st.session_state["email"] = user.email
            return True, f"Welcome back, {user.full_name}!"
        except Exception as exc:
            return False, f"Login failed: {exc}"
        finally:
            session.close()

    @staticmethod
    def logout():
        """Clear session state and log out user."""
        keys = ["authenticated", "user_id", "username", "full_name", "email"]
        for key in keys:
            st.session_state.pop(key, None)

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is logged in."""
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_user_id() -> int | None:
        """Return logged-in user id."""
        return st.session_state.get("user_id")

    @staticmethod
    def require_auth():
        """Redirect to login if not authenticated."""
        if not AuthManager.is_authenticated():
            st.warning("Please login to access this page.")
            st.stop()
