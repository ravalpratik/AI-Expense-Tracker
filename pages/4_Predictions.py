"""ML Spending Prediction page."""

import streamlit as st
import pandas as pd
from auth import AuthManager
from expense import ExpenseManager
from prediction import SpendingPredictor
from utils import apply_custom_css, format_currency


def render():
    AuthManager.require_auth()
    apply_custom_css(st.session_state.get("dark_mode", True))

    user_id = AuthManager.get_user_id()
    predictor = SpendingPredictor(user_id)
    em = ExpenseManager(user_id)

    st.markdown('<p class="page-header">🔮 Spending Predictions</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Machine Learning powered next-month spending forecast</p>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    **ML Workflow:** Data Collection → Cleaning → Feature Engineering →
    Train/Test Split → Model Training → Evaluation → Prediction
    """)

    col1, col2 = st.columns(2)
    with col1:
        train_btn = st.button("🔄 Train / Retrain Models", type="primary", use_container_width=True)
    with col2:
        predict_btn = st.button("📈 Predict Next Month", use_container_width=True)

    user_df = em.get_expenses_df()
    if not user_df.empty:
        user_df = user_df.rename(columns={"date": "Date", "amount": "Amount", "category": "Category"})
        user_df["Date"] = pd.to_datetime(user_df["Date"])
        st.caption(f"Using {len(user_df)} expense records from your account.")
    else:
        st.caption("No personal data yet – training will use the sample dataset.")

    if train_btn:
        with st.spinner("Training models..."):
            df = user_df if len(user_df) >= 20 else None
            metrics = predictor.train(df)
            if "error" in metrics:
                st.warning(metrics["error"])
            else:
                st.session_state["ml_metrics"] = metrics
                st.success(f"Best model: **{predictor.best_model_name}**")

    if predict_btn or "ml_metrics" in st.session_state:
        with st.spinner("Generating prediction..."):
            df = user_df if not user_df.empty else None
            result = predictor.predict_next_month(df)

            if "error" in result:
                st.warning(result["error"])
            else:
                st.subheader(f"📅 Prediction for {result['prediction_month']}")

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Predicted Spending", format_currency(result["predicted_amount"]))
                with m2:
                    st.metric("Previous Month", format_currency(result["previous_month"]))
                with m3:
                    change = result["change_pct"]
                    st.metric("Change", f"{change:+.1f}%")

                if result["change_pct"] > 0:
                    st.warning(
                        f"Predicted spending is {result['change_pct']:.1f}% higher than last month."
                    )
                elif result["change_pct"] < 0:
                    st.success(
                        f"Predicted spending is {abs(result['change_pct']):.1f}% lower than last month."
                    )

    # Model comparison
    metrics = st.session_state.get("ml_metrics") or predictor.metrics
    if metrics and "error" not in metrics:
        st.subheader("📊 Model Comparison")
        metrics_df = pd.DataFrame([
            {"Model": name, "MAE (₹)": v["MAE"], "R² Score": v["R2"]}
            for name, v in metrics.items()
        ])
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        best = max(metrics.items(), key=lambda x: x[1]["R2"])
        st.info(f"🏆 Best performing model: **{best[0]}** (R² = {best[1]['R2']:.4f})")

    with st.expander("ℹ️ About the ML Pipeline"):
        st.markdown("""
        **Features used:** month, year, previous month total, 3-month average,
        food/travel/shopping percentages, expense count.

        **Models compared:**
        - Linear Regression
        - Random Forest Regressor
        - Decision Tree Regressor

        The best model (highest R² score) is saved to `models/spending_model.pkl`.
        """)
