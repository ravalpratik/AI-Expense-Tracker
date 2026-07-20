"""
Expense management module – CRUD operations and queries.
"""

from datetime import date, datetime
from typing import Optional
import pandas as pd
from sqlalchemy import and_, extract, func, or_
from database import get_session, Expense

CATEGORIES = [
    "Food", "Travel", "Shopping", "Medical", "Bills",
    "Education", "Entertainment", "Other",
]

PAYMENT_MODES = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]


class ExpenseManager:
    """Manages expense CRUD and analytics queries for a user."""

    def __init__(self, user_id: int):
        self.user_id = user_id

    def add_expense(
        self,
        expense_date: date,
        amount: float,
        category: str,
        description: str = "",
        payment_mode: str = "Cash",
    ) -> tuple[bool, str]:
        """Add a new expense record."""
        if amount <= 0:
            return False, "Amount must be greater than zero."
        if category not in CATEGORIES:
            return False, "Invalid category."
        session = get_session()
        try:
            expense = Expense(
                user_id=self.user_id,
                date=expense_date,
                amount=round(float(amount), 2),
                category=category,
                description=description.strip(),
                payment_mode=payment_mode,
            )
            session.add(expense)
            session.commit()
            return True, "Expense added successfully."
        except Exception as exc:
            session.rollback()
            return False, f"Failed to add expense: {exc}"
        finally:
            session.close()

    def update_expense(
        self,
        expense_id: int,
        expense_date: date,
        amount: float,
        category: str,
        description: str = "",
        payment_mode: str = "Cash",
    ) -> tuple[bool, str]:
        """Update an existing expense."""
        if amount <= 0:
            return False, "Amount must be greater than zero."
        session = get_session()
        try:
            expense = session.query(Expense).filter(
                Expense.id == expense_id, Expense.user_id == self.user_id
            ).first()
            if not expense:
                return False, "Expense not found."
            expense.date = expense_date
            expense.amount = round(float(amount), 2)
            expense.category = category
            expense.description = description.strip()
            expense.payment_mode = payment_mode
            expense.updated_at = datetime.utcnow()
            session.commit()
            return True, "Expense updated successfully."
        except Exception as exc:
            session.rollback()
            return False, f"Failed to update expense: {exc}"
        finally:
            session.close()

    def delete_expense(self, expense_id: int) -> tuple[bool, str]:
        """Delete an expense by id."""
        session = get_session()
        try:
            expense = session.query(Expense).filter(
                Expense.id == expense_id, Expense.user_id == self.user_id
            ).first()
            if not expense:
                return False, "Expense not found."
            session.delete(expense)
            session.commit()
            return True, "Expense deleted successfully."
        except Exception as exc:
            session.rollback()
            return False, f"Failed to delete expense: {exc}"
        finally:
            session.close()

    def get_expenses_df(
        self,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> pd.DataFrame:
        """Return expenses as a pandas DataFrame with optional filters."""
        session = get_session()
        try:
            query = session.query(Expense).filter(Expense.user_id == self.user_id)
            if category and category != "All":
                query = query.filter(Expense.category == category)
            if start_date:
                query = query.filter(Expense.date >= start_date)
            if end_date:
                query = query.filter(Expense.date <= end_date)
            if search:
                term = f"%{search.strip()}%"
                query = query.filter(
                    or_(Expense.description.ilike(term), Expense.category.ilike(term))
                )
            expenses = query.order_by(Expense.date.desc()).all()
            if not expenses:
                return pd.DataFrame(columns=[
                    "id", "date", "amount", "category", "description", "payment_mode"
                ])
            records = [
                {
                    "id": e.id,
                    "date": e.date,
                    "amount": e.amount,
                    "category": e.category,
                    "description": e.description,
                    "payment_mode": e.payment_mode,
                }
                for e in expenses
            ]
            return pd.DataFrame(records)
        finally:
            session.close()

    def get_total_expenses(self) -> float:
        """Return lifetime total expenses."""
        session = get_session()
        try:
            total = session.query(func.sum(Expense.amount)).filter(
                Expense.user_id == self.user_id
            ).scalar()
            return float(total or 0)
        finally:
            session.close()

    def get_monthly_total(self, month: int, year: int) -> float:
        """Return total expenses for a given month."""
        session = get_session()
        try:
            total = session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.user_id == self.user_id,
                    extract("month", Expense.date) == month,
                    extract("year", Expense.date) == year,
                )
            ).scalar()
            return float(total or 0)
        finally:
            session.close()

    def get_today_total(self) -> float:
        """Return today's total expenses."""
        today = date.today()
        session = get_session()
        try:
            total = session.query(func.sum(Expense.amount)).filter(
                and_(Expense.user_id == self.user_id, Expense.date == today)
            ).scalar()
            return float(total or 0)
        finally:
            session.close()

    def get_category_breakdown(self, month: int = None, year: int = None) -> pd.DataFrame:
        """Return category-wise spending totals."""
        session = get_session()
        try:
            query = session.query(
                Expense.category,
                func.sum(Expense.amount).label("total"),
            ).filter(Expense.user_id == self.user_id)
            if month and year:
                query = query.filter(
                    and_(
                        extract("month", Expense.date) == month,
                        extract("year", Expense.date) == year,
                    )
                )
            results = query.group_by(Expense.category).all()
            if not results:
                return pd.DataFrame(columns=["category", "total"])
            return pd.DataFrame([{"category": r[0], "total": float(r[1])} for r in results])
        finally:
            session.close()

    def get_recent_transactions(self, limit: int = 5) -> pd.DataFrame:
        """Return most recent expense transactions."""
        df = self.get_expenses_df()
        return df.head(limit) if not df.empty else df
