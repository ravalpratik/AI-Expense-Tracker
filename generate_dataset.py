"""
Generate a realistic sample expense dataset (500–1000 records).
Run: python generate_dataset.py
"""

import os
import random
from datetime import date, timedelta
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT = os.path.join(DATA_DIR, "sample_expenses.csv")

CATEGORIES = ["Food", "Travel", "Shopping", "Medical", "Bills", "Education", "Entertainment", "Other"]
PAYMENT_MODES = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]

DESCRIPTIONS = {
    "Food": ["Grocery shopping", "Restaurant dinner", "Coffee shop", "Fast food", "Home delivery", "Snacks"],
    "Travel": ["Cab ride", "Bus ticket", "Fuel", "Train ticket", "Auto rickshaw", "Parking fee"],
    "Shopping": ["Clothing", "Electronics", "Accessories", "Footwear", "Online order", "Gift purchase"],
    "Medical": ["Pharmacy", "Doctor visit", "Lab test", "Medicines", "Health checkup"],
    "Bills": ["Electricity bill", "Internet bill", "Mobile recharge", "Water bill", "Gas bill", "Rent"],
    "Education": ["Books", "Course fee", "Stationery", "Online course", "Exam fee"],
    "Entertainment": ["Movie ticket", "Streaming subscription", "Concert", "Gaming", "Sports event"],
    "Other": ["Miscellaneous", "Donation", "Repair", "Personal care", "Pet supplies"],
}

# Category amount ranges (min, max) in INR
AMOUNT_RANGES = {
    "Food": (50, 2500),
    "Travel": (30, 3000),
    "Shopping": (200, 15000),
    "Medical": (100, 5000),
    "Bills": (500, 8000),
    "Education": (200, 10000),
    "Entertainment": (100, 3000),
    "Other": (50, 2000),
}


def generate_expenses(num_records: int = 800, num_users: int = 5) -> pd.DataFrame:
    """Generate realistic expense records spanning 18 months."""
    random.seed(42)
    np.random.seed(42)

    records = []
    start_date = date(2024, 1, 1)
    end_date = date(2025, 6, 30)
    total_days = (end_date - start_date).days

    for _ in range(num_records):
        user_id = random.randint(1, num_users)
        expense_date = start_date + timedelta(days=random.randint(0, total_days))
        category = random.choices(
            CATEGORIES,
            weights=[25, 10, 15, 8, 12, 7, 13, 10],
        )[0]
        lo, hi = AMOUNT_RANGES[category]
        amount = round(random.uniform(lo, hi), 2)
        description = random.choice(DESCRIPTIONS[category])
        payment_mode = random.choices(
            PAYMENT_MODES,
            weights=[10, 35, 15, 20, 10, 10],
        )[0]

        records.append({
            "Date": expense_date.strftime("%Y-%m-%d"),
            "Category": category,
            "Amount": amount,
            "Month": expense_date.month,
            "Year": expense_date.year,
            "Payment Mode": payment_mode,
            "Description": description,
            "User ID": user_id,
        })

    df = pd.DataFrame(records)
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    df = generate_expenses(num_records=800)
    df.to_csv(OUTPUT, index=False)
    print(f"Generated {len(df)} expense records -> {OUTPUT}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Total amount: INR {df['Amount'].sum():,.2f}")
    print(f"Categories:\n{df.groupby('Category')['Amount'].sum().sort_values(ascending=False)}")


if __name__ == "__main__":
    main()
