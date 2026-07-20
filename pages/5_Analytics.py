"""Analytics page – interactive Plotly charts."""

import streamlit as st
from auth import AuthManager
from expense import ExpenseManager
from charts import ChartGenerator
from utils import apply_custom_css


def render():
    AuthManager.require_auth()
    apply_custom_css(st.session_state.get("dark_mode", True))

    user_id = AuthManager.get_user_id()
    em = ExpenseManager(user_id)
    df = em.get_expenses_df()

    st.markdown('<p class="page-header">📈 Analytics</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Interactive charts and spending visualizations</p>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No expense data available. Add expenses to see analytics.")
        return

    dark = st.session_state.get("dark_mode", True)
    charts = ChartGenerator(df, dark_mode=dark)

    tab1, tab2, tab3 = st.tabs(["📊 Trends", "🍕 Categories", "📅 Comparisons"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.monthly_trend(), use_container_width=True)
        with c2:
            st.plotly_chart(charts.daily_expenses(), use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.category_pie(), use_container_width=True)
        with c2:
            st.plotly_chart(charts.top_categories(), use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.weekly_expenses(), use_container_width=True)
        with c2:
            st.plotly_chart(charts.monthly_comparison(), use_container_width=True)
