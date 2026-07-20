"""
Utility functions – theming, formatting, validation, AI insights.
"""

from datetime import date
import pandas as pd
import streamlit as st


def init_session_defaults():
    """Initialize default session state values."""
    defaults = {
        "authenticated": False,
        "dark_mode": True,
        "user_id": None,
        "username": None,
        "full_name": None,
        "email": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def format_currency(amount: float) -> str:
    """Format amount as Indian Rupees."""
    return f"₹{amount:,.2f}"


def apply_custom_css(dark_mode: bool = True):
    """Inject professional custom CSS for dark/light themes."""
    if dark_mode:
        bg = "#0f172a"
        card = "#1e293b"
        text = "#f1f5f9"
        muted = "#94a3b8"
        accent = "#6366f1"
        accent2 = "#818cf8"
        border = "#334155"
    else:
        bg = "#f8fafc"
        card = "#ffffff"
        text = "#0f172a"
        muted = "#64748b"
        accent = "#4f46e5"
        accent2 = "#6366f1"
        border = "#e2e8f0"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background-color: {bg};
            color: {text};
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {card} 0%, {bg} 100%);
            border-right: 1px solid {border};
        }}

        .metric-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
        }}

        .metric-label {{
            color: {muted};
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }}

        .metric-value {{
            color: {text};
            font-size: 1.75rem;
            font-weight: 700;
        }}

        .metric-icon {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .page-header {{
            font-size: 2rem;
            font-weight: 700;
            color: {text};
            margin-bottom: 0.25rem;
        }}

        .page-subtitle {{
            color: {muted};
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }}

        .insight-card {{
            background: linear-gradient(135deg, {accent}22, {accent2}11);
            border: 1px solid {accent}44;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            color: {text};
        }}

        .alert-warning {{
            background: #f59e0b22;
            border-left: 4px solid #f59e0b;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }}

        .alert-critical {{
            background: #ef444422;
            border-left: 4px solid #ef4444;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }}

        div[data-testid="stMetric"] {{
            background: {card};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1rem;
        }}

        .stButton > button {{
            border-radius: 10px;
            font-weight: 600;
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {accent}, {accent2});
            border: none;
        }}

        h1, h2, h3, h4, h5, h6, p, label, span {{
            color: {text};
        }}

        .auth-container {{
            max-width: 420px;
            margin: 2rem auto;
            padding: 2rem;
            background: {card};
            border-radius: 20px;
            border: 1px solid {border};
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}

        .brand-title {{
            text-align: center;
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, {accent}, {accent2});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        [data-testid="stSidebarNav"] {{
            display: none;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(icon: str, label: str, value: str, color: str = "#6366f1"):
    """Render a styled metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def generate_ai_insights(expense_df: pd.DataFrame, monthly_totals: dict) -> list[str]:
    """
    Generate intelligent spending insights using statistical analysis.
    Returns a list of insight strings.
    """
    insights = []
    if expense_df.empty:
        insights.append("Start adding expenses to receive personalized AI insights.")
        return insights

    today = date.today()
    current_month = today.month
    current_year = today.year

    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1

    current_total = monthly_totals.get((current_year, current_month), 0)
    prev_total = monthly_totals.get((prev_year, prev_month), 0)

    if prev_total > 0:
        change_pct = ((current_total - prev_total) / prev_total) * 100
        direction = "more" if change_pct > 0 else "less"
        insights.append(
            f"You spent {abs(change_pct):.0f}% {direction} overall than last month "
            f"({format_currency(current_total)} vs {format_currency(prev_total)})."
        )

    expense_df = expense_df.copy()
    expense_df["date"] = pd.to_datetime(expense_df["date"])
    expense_df["month"] = expense_df["date"].dt.month
    expense_df["year"] = expense_df["date"].dt.year

    current_df = expense_df[
        (expense_df["month"] == current_month) & (expense_df["year"] == current_year)
    ]
    prev_df = expense_df[
        (expense_df["month"] == prev_month) & (expense_df["year"] == prev_year)
    ]

    for category in current_df["category"].unique():
        curr_cat = current_df[current_df["category"] == category]["amount"].sum()
        prev_cat = prev_df[prev_df["category"] == category]["amount"].sum()
        if prev_cat > 0:
            cat_change = ((curr_cat - prev_cat) / prev_cat) * 100
            if abs(cat_change) >= 15:
                if cat_change > 0:
                    insights.append(
                        f"{category} expenses increased by {cat_change:.0f}% "
                        f"compared to last month."
                    )
                else:
                    insights.append(
                        f"{category} expenses are {abs(cat_change):.0f}% below last month – great job!"
                    )

    avg_monthly = expense_df.groupby(["year", "month"])["amount"].sum().mean()
    if current_total < avg_monthly:
        savings = avg_monthly - current_total
        insights.append(
            f"You can save approximately {format_currency(savings)} this month "
            f"if you maintain current spending levels."
        )

    top_category = current_df.groupby("category")["amount"].sum()
    if not top_category.empty:
        top = top_category.idxmax()
        top_amt = top_category.max()
        if current_total > 0:
            pct = (top_amt / current_total) * 100
            insights.append(
                f"Your top spending category is {top} at {pct:.0f}% of this month's budget."
            )

    if not insights:
        insights.append("Your spending patterns look stable. Keep tracking for better insights!")

    return insights[:6]
