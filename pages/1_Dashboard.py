"""Dashboard page – overview metrics, recent transactions, category breakdown."""

import streamlit as st
import plotly.express as px
from auth import AuthManager
from expense import ExpenseManager
from budget import BudgetManager
from utils import render_metric_card, format_currency, generate_ai_insights, apply_custom_css
from datetime import date


def render():
    AuthManager.require_auth()
    apply_custom_css(st.session_state.get("dark_mode", True))

    user_id = AuthManager.get_user_id()
    em = ExpenseManager(user_id)
    bm = BudgetManager(user_id)

    today = date.today()
    budget_status = bm.get_budget_status(today.month, today.year)

    st.markdown('<p class="page-header">📊 Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Your financial overview at a glance</p>',
        unsafe_allow_html=True,
    )

    # Budget alerts
    if budget_status["alert_message"]:
        css_class = "alert-critical" if budget_status["status"] == "critical" else "alert-warning"
        st.markdown(
            f'<div class="{css_class}">{budget_status["alert_message"]}</div>',
            unsafe_allow_html=True,
        )

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("💸", "Total Expenses", format_currency(em.get_total_expenses()))
    with col2:
        render_metric_card(
            "📅", "This Month",
            format_currency(em.get_monthly_total(today.month, today.year)),
            "#8b5cf6",
        )
    with col3:
        render_metric_card("☀️", "Today", format_currency(em.get_today_total()), "#22c55e")
    with col4:
        remaining = budget_status["remaining"]
        color = "#ef4444" if remaining < 0 else "#06b6d4"
        render_metric_card("🎯", "Remaining Budget", format_currency(remaining), color)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📋 Recent Transactions")
        recent = em.get_recent_transactions(8)
        if recent.empty:
            st.info("No transactions yet. Add your first expense!")
        else:
            display = recent.copy()
            display["amount"] = display["amount"].apply(format_currency)
            display["date"] = display["date"].astype(str)
            st.dataframe(
                display[["date", "category", "description", "amount", "payment_mode"]],
                use_container_width=True,
                hide_index=True,
            )

    with col_right:
        st.subheader("🍕 Expense by Category")
        cat_df = em.get_category_breakdown(today.month, today.year)
        if cat_df.empty:
            st.info("No category data for this month.")
        else:
            dark = st.session_state.get("dark_mode", True)
            fig = px.pie(
                cat_df, values="total", names="category",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            layout = dict(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f1f5f9" if dark else "#0f172a"),
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                height=320,
            )
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    # AI Insights
    st.subheader("🤖 AI Insights")
    all_expenses = em.get_expenses_df()
    if not all_expenses.empty:
        all_expenses["date"] = all_expenses["date"].astype(str)
        import pandas as pd
        all_expenses["date"] = pd.to_datetime(all_expenses["date"])
        monthly_totals = {}
        for (y, m), grp in all_expenses.groupby([
            all_expenses["date"].dt.year, all_expenses["date"].dt.month
        ]):
            monthly_totals[(y, m)] = grp["amount"].sum()
        insights = generate_ai_insights(all_expenses, monthly_totals)
        for insight in insights:
            st.markdown(f'<div class="insight-card">💡 {insight}</div>', unsafe_allow_html=True)
    else:
        st.info("Add expenses to unlock AI-powered insights.")

    # Budget progress
    if budget_status["budget"] > 0:
        st.subheader("📈 Budget Usage")
        st.progress(min(budget_status["usage_pct"] / 100, 1.0))
        st.caption(
            f"Used {budget_status['usage_pct']:.1f}% "
            f"({format_currency(budget_status['spent'])} of {format_currency(budget_status['budget'])})"
        )
