"""
Budget management module – set budgets, track usage, generate alerts.
"""

from datetime import date
from database import get_session, Budget
from expense import ExpenseManager


class BudgetManager:
    """Manages monthly budgets and spending alerts."""

    WARNING_THRESHOLD = 80
    CRITICAL_THRESHOLD = 100

    SUGGESTIONS = {
        "Food": "Consider cooking at home more often to reduce food spending.",
        "Shopping": "Try a 24-hour rule before non-essential purchases.",
        "Entertainment": "Look for free or low-cost entertainment alternatives.",
        "Travel": "Use public transport or carpool to cut travel costs.",
        "Medical": "Compare prices across pharmacies for regular medications.",
        "Bills": "Review subscriptions and cancel unused services.",
        "Education": "Look for free online courses and library resources.",
        "Other": "Track miscellaneous expenses to identify unnecessary spending.",
    }

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.expense_manager = ExpenseManager(user_id)

    def set_budget(self, amount: float, month: int = None, year: int = None) -> tuple[bool, str]:
        """Set or update monthly budget."""
        if amount <= 0:
            return False, "Budget must be greater than zero."
        today = date.today()
        month = month or today.month
        year = year or today.year

        session = get_session()
        try:
            existing = session.query(Budget).filter(
                Budget.user_id == self.user_id,
                Budget.month == month,
                Budget.year == year,
            ).first()
            if existing:
                existing.amount = round(float(amount), 2)
            else:
                budget = Budget(
                    user_id=self.user_id,
                    month=month,
                    year=year,
                    amount=round(float(amount), 2),
                )
                session.add(budget)
            session.commit()
            return True, f"Budget set to ₹{amount:,.2f} for {month}/{year}."
        except Exception as exc:
            session.rollback()
            return False, f"Failed to set budget: {exc}"
        finally:
            session.close()

    def get_budget(self, month: int = None, year: int = None) -> float:
        """Get budget for a month, default 0 if not set."""
        today = date.today()
        month = month or today.month
        year = year or today.year
        session = get_session()
        try:
            budget = session.query(Budget).filter(
                Budget.user_id == self.user_id,
                Budget.month == month,
                Budget.year == year,
            ).first()
            return float(budget.amount) if budget else 0.0
        finally:
            session.close()

    def get_budget_status(self, month: int = None, year: int = None) -> dict:
        """
        Return budget usage status with alerts and suggestions.
        """
        today = date.today()
        month = month or today.month
        year = year or today.year

        budget = self.get_budget(month, year)
        spent = self.expense_manager.get_monthly_total(month, year)
        remaining = budget - spent
        usage_pct = (spent / budget * 100) if budget > 0 else 0

        status = "normal"
        alert_message = None
        if budget > 0:
            if usage_pct >= self.CRITICAL_THRESHOLD:
                status = "critical"
                alert_message = "Critical: You have exceeded your monthly budget!"
            elif usage_pct >= self.WARNING_THRESHOLD:
                status = "warning"
                alert_message = f"Warning: You have used {usage_pct:.0f}% of your budget."

        suggestions = self._generate_suggestions(month, year)

        return {
            "budget": budget,
            "spent": spent,
            "remaining": remaining,
            "usage_pct": round(usage_pct, 1),
            "status": status,
            "alert_message": alert_message,
            "suggestions": suggestions,
        }

    def _generate_suggestions(self, month: int, year: int) -> list[str]:
        """Generate category-specific budget suggestions."""
        suggestions = []
        breakdown = self.expense_manager.get_category_breakdown(month, year)
        if breakdown.empty:
            return ["Set a monthly budget and start tracking expenses for personalized tips."]

        total = breakdown["total"].sum()
        if total == 0:
            return suggestions

        breakdown = breakdown.sort_values("total", ascending=False)
        top = breakdown.iloc[0]
        pct = (top["total"] / total) * 100

        if pct > 30:
            cat = top["category"]
            suggestions.append(
                f"{cat} accounts for {pct:.0f}% of spending. "
                f"{self.SUGGESTIONS.get(cat, 'Review this category for savings.')}"
            )

        budget = self.get_budget(month, year)
        spent = self.expense_manager.get_monthly_total(month, year)

        if budget > 0 and spent / budget >= 0.8:
            suggestions.append("Avoid unnecessary expenses until month end.")
            suggestions.append("Reduce discretionary spending on shopping and entertainment.")

        if not suggestions:
            suggestions.append("Your spending is well balanced. Keep it up!")

        return suggestions[:4]
