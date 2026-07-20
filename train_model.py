"""
Machine Learning training script.
Trains and compares models, saves the best one to models/spending_model.pkl.

Run: python train_model.py
"""

import os
import pandas as pd
from prediction import SpendingPredictor, SAMPLE_CSV

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("=" * 60)
    print("AI Expense Tracker – ML Model Training")
    print("=" * 60)

    if not os.path.exists(SAMPLE_CSV):
        print("Sample dataset not found. Generating...")
        from generate_dataset import main as gen_main
        gen_main()

    df = pd.read_csv(SAMPLE_CSV, parse_dates=["Date"])
    print(f"\nLoaded {len(df)} records from {SAMPLE_CSV}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")

    predictor = SpendingPredictor()
    print("\n--- Training Models ---")
    metrics = predictor.train(df)

    if "error" in metrics:
        print(f"Error: {metrics['error']}")
        return

    print("\n--- Model Comparison ---")
    print(f"{'Model':<25} {'MAE (INR)':<12} {'R2 Score':<10}")
    print("-" * 47)
    for name, scores in metrics.items():
        print(f"{name:<25} {scores['MAE']:<12.2f} {scores['R2']:<10.4f}")

    best = max(metrics.items(), key=lambda x: x[1]["R2"])
    print(f"\nBest Model: {best[0]} (R2 = {best[1]['R2']:.4f})")
    print(f"Model saved to models/spending_model.pkl")

    print("\n--- Next Month Prediction (Sample Data) ---")
    result = predictor.predict_next_month(df)
    if "error" not in result:
        print(f"Predicted: INR {result['predicted_amount']:,.2f}")
        print(f"Previous Month: INR {result['previous_month']:,.2f}")
        print(f"Change: {result['change_pct']:+.1f}%")

    print("\n" + "=" * 60)
    print("Training complete!")


if __name__ == "__main__":
    main()
