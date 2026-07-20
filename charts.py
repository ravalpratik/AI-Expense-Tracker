"""
Charts module – interactive Plotly visualizations for analytics.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLORS = [
    "#6366f1", "#8b5cf6", "#ec4899", "#f43f5e",
    "#f97316", "#eab308", "#22c55e", "#06b6d4",
]

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f1f5f9", family="Inter"),
    margin=dict(l=20, r=20, t=40, b=20),
)

LIGHT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#0f172a", family="Inter"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def _get_layout(dark_mode: bool = True) -> dict:
    return DARK_LAYOUT if dark_mode else LIGHT_LAYOUT


class ChartGenerator:
    """Generates Plotly charts from expense DataFrames."""

    def __init__(self, df: pd.DataFrame, dark_mode: bool = True):
        self.df = df.copy()
        self.dark_mode = dark_mode
        self.layout = _get_layout(dark_mode)
        if not self.df.empty:
            self.df["date"] = pd.to_datetime(self.df["date"])

    def monthly_trend(self) -> go.Figure:
        """Line chart of monthly spending trend."""
        if self.df.empty:
            return self._empty_chart("Monthly Spending Trend")
        monthly = self.df.groupby(
            self.df["date"].dt.to_period("M")
        )["amount"].sum().reset_index()
        monthly["date"] = monthly["date"].astype(str)
        fig = px.line(
            monthly, x="date", y="amount",
            title="Monthly Spending Trend",
            labels={"date": "Month", "amount": "Amount (₹)"},
            markers=True,
            color_discrete_sequence=["#6366f1"],
        )
        fig.update_layout(**self.layout)
        fig.update_traces(line=dict(width=3))
        return fig

    def category_pie(self) -> go.Figure:
        """Pie chart of category-wise spending."""
        if self.df.empty:
            return self._empty_chart("Category-wise Spending")
        cat = self.df.groupby("category")["amount"].sum().reset_index()
        fig = px.pie(
            cat, values="amount", names="category",
            title="Category-wise Spending",
            color_discrete_sequence=COLORS,
            hole=0.4,
        )
        fig.update_layout(**self.layout)
        return fig

    def daily_expenses(self) -> go.Figure:
        """Bar chart of daily expenses (last 30 days)."""
        if self.df.empty:
            return self._empty_chart("Daily Expenses")
        recent = self.df.sort_values("date").tail(30)
        daily = recent.groupby("date")["amount"].sum().reset_index()
        fig = px.bar(
            daily, x="date", y="amount",
            title="Daily Expenses (Last 30 Days)",
            labels={"date": "Date", "amount": "Amount (₹)"},
            color_discrete_sequence=["#8b5cf6"],
        )
        fig.update_layout(**self.layout)
        return fig

    def top_categories(self) -> go.Figure:
        """Horizontal bar chart of top spending categories."""
        if self.df.empty:
            return self._empty_chart("Top Spending Categories")
        cat = self.df.groupby("category")["amount"].sum().reset_index()
        cat = cat.sort_values("amount", ascending=True).tail(5)
        fig = px.bar(
            cat, x="amount", y="category", orientation="h",
            title="Top Spending Categories",
            labels={"amount": "Amount (₹)", "category": "Category"},
            color="amount",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(**self.layout, showlegend=False)
        return fig

    def weekly_expenses(self) -> go.Figure:
        """Bar chart of weekly spending."""
        if self.df.empty:
            return self._empty_chart("Weekly Expenses")
        df = self.df.copy()
        df["week"] = df["date"].dt.isocalendar().week.astype(str) + " (W)"
        df["year_week"] = df["date"].dt.strftime("%Y-W%U")
        weekly = df.groupby("year_week")["amount"].sum().reset_index()
        weekly = weekly.tail(8)
        fig = px.bar(
            weekly, x="year_week", y="amount",
            title="Weekly Expenses",
            labels={"year_week": "Week", "amount": "Amount (₹)"},
            color_discrete_sequence=["#06b6d4"],
        )
        fig.update_layout(**self.layout)
        return fig

    def monthly_comparison(self) -> go.Figure:
        """Grouped bar chart comparing last 6 months."""
        if self.df.empty:
            return self._empty_chart("Monthly Comparison")
        df = self.df.copy()
        df["month_label"] = df["date"].dt.strftime("%b %Y")
        monthly = df.groupby("month_label")["amount"].sum().reset_index()
        monthly = monthly.tail(6)
        fig = px.bar(
            monthly, x="month_label", y="amount",
            title="Monthly Comparison (Last 6 Months)",
            labels={"month_label": "Month", "amount": "Amount (₹)"},
            color="amount",
            color_continuous_scale="Plasma",
        )
        fig.update_layout(**self.layout, showlegend=False)
        return fig

    def _empty_chart(self, title: str) -> go.Figure:
        """Return placeholder chart when no data."""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#94a3b8"),
        )
        fig.update_layout(title=title, **self.layout, height=350)
        return fig
