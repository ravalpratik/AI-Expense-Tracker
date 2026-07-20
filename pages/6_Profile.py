"""Profile page – user info, budget settings, account stats."""

import streamlit as st
from datetime import date
from auth import AuthManager
from expense import ExpenseManager
from budget import BudgetManager
from utils import apply_custom_css, format_currency


def render():
    AuthManager.require_auth()
    apply_custom_css(st.session_state.get("dark_mode", True))

    user_id = AuthManager.get_user_id()
    em = ExpenseManager(user_id)
    bm = BudgetManager(user_id)

    st.markdown('<p class="page-header">👤 Profile & Budget</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Manage your account and monthly budget</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Account Information")
        st.write(f"**Name:** {st.session_state.get('full_name', 'N/A')}")
        st.write(f"**Username:** {st.session_state.get('username', 'N/A')}")
        st.write(f"**Email:** {st.session_state.get('email', 'N/A')}")

        st.divider()
        st.subheader("📊 Account Statistics")
        df = em.get_expenses_df()
        st.metric("Total Expenses Recorded", len(df))
        st.metric("Lifetime Spending", format_currency(em.get_total_expenses()))
        today = date.today()
        st.metric("This Month", format_currency(em.get_monthly_total(today.month, today.year)))

    with col2:
        st.subheader("🎯 Monthly Budget")
        today = date.today()
        current_budget = bm.get_budget(today.month, today.year)

        with st.form("budget_form"):
            budget_amount = st.number_input(
                "Set Monthly Budget (₹)",
                min_value=100.0,
                value=current_budget if current_budget > 0 else 10000.0,
                step=500.0,
            )
            b_month = st.selectbox(
                "Month", range(1, 13),
                index=today.month - 1,
                format_func=lambda x: date(2000, x, 1).strftime("%B"),
            )
            b_year = st.number_input("Year", min_value=2020, max_value=2030, value=today.year)
            submitted = st.form_submit_button("💾 Save Budget", type="primary", use_container_width=True)
            if submitted:
                ok, msg = bm.set_budget(budget_amount, b_month, b_year)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        status = bm.get_budget_status(today.month, today.year)
        if status["budget"] > 0:
            st.divider()
            st.subheader("📈 Budget Status")
            st.progress(min(status["usage_pct"] / 100, 1.0))
            st.write(f"**Spent:** {format_currency(status['spent'])}")
            st.write(f"**Remaining:** {format_currency(status['remaining'])}")
            st.write(f"**Usage:** {status['usage_pct']:.1f}%")

            if status["alert_message"]:
                st.warning(status["alert_message"])

            st.subheader("💡 Suggestions")
            for suggestion in status["suggestions"]:
                st.markdown(f"- {suggestion}")
