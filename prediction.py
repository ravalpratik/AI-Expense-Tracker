"""
Machine Learning spending prediction module.
Trains and compares Linear Regression, Random Forest, Decision Tree.
"""

import os
from datetime import date
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from database import get_session, Prediction
from expense import ExpenseManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(MODEL_DIR, "spending_model.pkl")
SAMPLE_CSV = os.path.join(DATA_DIR, "sample_expenses.csv")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


class SpendingPredictor:
    """ML pipeline for monthly spending prediction."""

    MODELS = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Decision Tree": DecisionTreeRegressor(random_state=42, max_depth=8),
    }

    FEATURE_COLS = [
        "month", "year", "prev_month_total", "avg_3_month",
        "food_pct", "travel_pct", "shopping_pct", "expense_count",
    ]

    def __init__(self, user_id: int = None):
        self.user_id = user_id
        self.best_model = None
        self.best_model_name = None
        self.metrics = {}

    @staticmethod
    def load_sample_data() -> pd.DataFrame:
        """Load sample CSV dataset."""
        if os.path.exists(SAMPLE_CSV):
            return pd.read_csv(SAMPLE_CSV, parse_dates=["Date"])
        return pd.DataFrame()

    def load_user_expenses(self) -> pd.DataFrame:
        """Load expenses for the current user from database."""
        if not self.user_id:
            return pd.DataFrame()
        manager = ExpenseManager(self.user_id)
        df = manager.get_expenses_df()
        if df.empty:
            return df
        df = df.rename(columns={"date": "Date", "amount": "Amount", "category": "Category"})
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering: aggregate monthly totals and derive features.
        """
        if df.empty:
            return pd.DataFrame()

        df = df.copy()
        df["Month"] = df["Date"].dt.month
        df["Year"] = df["Date"].dt.year

        monthly = df.groupby(["Year", "Month"]).agg(
            total=("Amount", "sum"),
            expense_count=("Amount", "count"),
        ).reset_index()

        monthly = monthly.sort_values(["Year", "Month"]).reset_index(drop=True)
        monthly["prev_month_total"] = monthly["total"].shift(1).fillna(monthly["total"].mean())
        monthly["avg_3_month"] = monthly["total"].rolling(3, min_periods=1).mean()

        for cat in ["Food", "Travel", "Shopping"]:
            cat_monthly = df[df["Category"] == cat].groupby(["Year", "Month"])["Amount"].sum()
            cat_monthly = cat_monthly.reset_index().rename(columns={"Amount": f"{cat.lower()}_total"})
            monthly = monthly.merge(cat_monthly, on=["Year", "Month"], how="left")
            monthly[f"{cat.lower()}_total"] = monthly[f"{cat.lower()}_total"].fillna(0)
            monthly[f"{cat.lower()}_pct"] = (
                monthly[f"{cat.lower()}_total"] / monthly["total"].replace(0, 1) * 100
            )

        monthly = monthly.rename(columns={"Month": "month", "Year": "year", "total": "target"})
        return monthly

    def train(self, df: pd.DataFrame = None) -> dict:
        """
        Train all models, compare accuracy, save best model.
        Returns metrics dict for each model.
        """
        if df is None:
            df = self.load_sample_data()
            if df.empty:
                df = self.load_user_expenses()

        prepared = self.prepare_data(df)
        if len(prepared) < 5:
            return {"error": "Insufficient data. Need at least 5 months of expenses."}

        X = prepared[self.FEATURE_COLS].fillna(0)
        y = prepared["target"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        best_r2 = -np.inf
        results = {}

        for name, model in self.MODELS.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            results[name] = {"MAE": round(mae, 2), "R2": round(r2, 4)}

            if r2 > best_r2:
                best_r2 = r2
                self.best_model = model
                self.best_model_name = name

        self.metrics = results

        if self.best_model:
            joblib.dump(
                {
                    "model": self.best_model,
                    "model_name": self.best_model_name,
                    "features": self.FEATURE_COLS,
                    "metrics": results,
                },
                MODEL_PATH,
            )

        return results

    def load_model(self) -> bool:
        """Load saved model from disk."""
        if not os.path.exists(MODEL_PATH):
            return False
        data = joblib.load(MODEL_PATH)
        self.best_model = data["model"]
        self.best_model_name = data["model_name"]
        self.metrics = data.get("metrics", {})
        return True

    def predict_next_month(self, df: pd.DataFrame = None) -> dict:
        """Predict next month's total spending."""
        if self.best_model is None:
            if not self.load_model():
                train_result = self.train(df)
                if "error" in train_result:
                    return train_result

        if df is None:
            df = self.load_user_expenses()
            if df.empty:
                df = self.load_sample_data()

        prepared = self.prepare_data(df)
        if prepared.empty:
            return {"error": "No data available for prediction."}

        last_row = prepared.iloc[-1]
        today = date.today()
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1

        features = pd.DataFrame([{
            "month": next_month,
            "year": next_year,
            "prev_month_total": last_row.get("target", 0),
            "avg_3_month": last_row.get("avg_3_month", 0),
            "food_pct": last_row.get("food_pct", 0),
            "travel_pct": last_row.get("travel_pct", 0),
            "shopping_pct": last_row.get("shopping_pct", 0),
            "expense_count": last_row.get("expense_count", 0),
        }])

        prediction = float(self.best_model.predict(features[self.FEATURE_COLS])[0])
        prev_month_total = float(last_row.get("target", 0))

        result = {
            "predicted_amount": round(max(prediction, 0), 2),
            "previous_month": round(prev_month_total, 2),
            "model_name": self.best_model_name,
            "change_pct": round(
                ((prediction - prev_month_total) / prev_month_total * 100)
                if prev_month_total > 0 else 0, 1
            ),
            "prediction_month": f"{next_year}-{next_month:02d}",
            "metrics": self.metrics,
        }

        if self.user_id:
            self._save_prediction(result)

        return result

    def _save_prediction(self, result: dict):
        """Store prediction in database."""
        session = get_session()
        try:
            best_r2 = 0
            if result.get("metrics") and self.best_model_name:
                best_r2 = result["metrics"].get(self.best_model_name, {}).get("R2", 0)
            pred = Prediction(
                user_id=self.user_id,
                predicted_amount=result["predicted_amount"],
                model_name=result["model_name"],
                accuracy=best_r2,
                prediction_month=result["prediction_month"],
            )
            session.add(pred)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
