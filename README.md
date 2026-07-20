# AI Expense Tracker

**BCA 5th Semester – Artificial Intelligence Major Project**

An AI-powered expense tracking application with OCR bill scanning, machine learning spending predictions, interactive analytics, and intelligent budget alerts.

---

## Features

| Feature | Description |
|---------|-------------|
| **User Authentication** | Registration, login, logout with bcrypt password hashing |
| **Dashboard** | Total/monthly/today expenses, budget status, recent transactions, AI insights |
| **Expense Management** | Add, edit, delete, search, filter by category and date |
| **OCR Bill Scanner** | Upload bills – EasyOCR extracts store, date, amount, items |
| **ML Predictions** | Predict next month's spending using Linear Regression, Random Forest, Decision Tree |
| **Budget Alerts** | Set monthly budget, warnings at 80%, critical at 100% |
| **Analytics** | Interactive Plotly charts – trends, categories, weekly/monthly comparisons |
| **AI Insights** | Statistical analysis with personalized spending suggestions |
| **Dark/Light Mode** | Professional modern UI with theme toggle |

---

## Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.12+
- **Database:** SQLite with SQLAlchemy ORM
- **ML:** scikit-learn, joblib
- **OCR:** EasyOCR
- **Charts:** Plotly
- **Auth:** bcrypt

---

## Project Structure

```
AI Expense Tracker/
├── app.py                  # Main application entry point
├── database.py             # SQLAlchemy models & DB setup
├── auth.py                 # Authentication module
├── expense.py              # Expense CRUD operations
├── ocr.py                  # OCR bill scanner
├── prediction.py           # ML prediction pipeline
├── charts.py               # Plotly chart generators
├── budget.py               # Budget management & alerts
├── utils.py                # Theming, formatting, AI insights
├── generate_dataset.py     # Sample dataset generator
├── train_model.py          # ML model training script
├── requirements.txt
├── README.md
├── database/
│   └── expense.db          # SQLite database (auto-created)
├── models/
│   └── spending_model.pkl  # Trained ML model
├── data/
│   └── sample_expenses.csv # Sample dataset (800 records)
├── uploads/                # Scanned bill images
├── assets/                 # Static assets
└── pages/
    ├── 1_Dashboard.py
    ├── 2_Add_Expense.py
    ├── 3_OCR_Bill_Scanner.py
    ├── 4_Predictions.py
    ├── 5_Analytics.py
    └── 6_Profile.py
```

---

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Steps

1. **Clone or download the project**
   ```bash
   cd "AI Expense Tracker"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate sample dataset**
   ```bash
   python generate_dataset.py
   ```

5. **Train the ML model**
   ```bash
   python train_model.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. Open **http://localhost:8501** in your browser.

---

## Usage Guide

### First Time Setup

1. Register a new account on the login page.
2. Go to **Profile** and set your monthly budget.
3. Add expenses manually or scan bills via **OCR Scanner**.
4. Visit **Predictions** to train models and view forecasts.
5. Explore **Analytics** for interactive charts.

### OCR Bill Scanner

1. Navigate to **OCR Scanner**.
2. Upload a bill image (PNG, JPG, JPEG).
3. Click **Scan Bill** – EasyOCR extracts details.
4. Review and edit extracted values.
5. Save as expense or bill record.

### ML Predictions

1. Navigate to **Predictions**.
2. Click **Train / Retrain Models** to compare algorithms.
3. Click **Predict Next Month** for the forecast.
4. View model accuracy (MAE, R²) comparison table.

---

## Database Schema

| Table | Fields |
|-------|--------|
| **users** | id, username, email, password_hash, full_name, created_at |
| **expenses** | id, user_id, date, amount, category, description, payment_mode |
| **bills** | id, user_id, store_name, bill_date, total_amount, items, image_path |
| **predictions** | id, user_id, predicted_amount, model_name, accuracy, prediction_month |
| **budgets** | id, user_id, month, year, amount |

---

## Machine Learning Pipeline

```
Data Collection → Cleaning → Feature Engineering → Train/Test Split
    → Model Training → Model Evaluation → Save Model → Prediction → Display
```

**Models Compared:**
- Linear Regression
- Random Forest Regressor
- Decision Tree Regressor

**Features:** month, year, previous month total, 3-month average, category percentages, expense count.

**Evaluation Metrics:** Mean Absolute Error (MAE), R² Score.

---

## Screenshots

> Add screenshots after running the application:
> - Login / Registration page
> - Dashboard with metrics and charts
> - OCR Bill Scanner with extracted data
> - ML Predictions with model comparison
> - Analytics charts
> - Profile & Budget settings

---

## Future Scope

- Integration with bank APIs for automatic transaction import
- Mobile app (Flutter/React Native)
- Multi-currency support
- Expense sharing for groups/families
- Advanced NLP for receipt item categorization
- Deep learning models (LSTM) for time-series prediction
- Export reports as PDF/Excel
- Email/SMS budget alerts
- Voice-based expense entry

---

## Project Report Outline

1. **Introduction** – Problem statement, objectives, scope
2. **Literature Survey** – Existing expense trackers, AI/ML in finance
3. **System Analysis** – Requirements (functional & non-functional), feasibility
4. **System Design** – Architecture diagram, ER diagram, data flow, UI design
5. **Implementation** – Modules, technologies, algorithms (OCR, ML)
6. **Testing** – Unit tests, integration tests, user acceptance
7. **Results** – Screenshots, model accuracy, performance metrics
8. **Conclusion** – Summary, learnings, future enhancements
9. **References** – Books, papers, documentation
10. **Appendix** – Source code listing, sample outputs

---

## Educational Concepts Demonstrated

- Python Programming & OOP
- Database Management (SQLite + SQLAlchemy)
- Artificial Intelligence & Machine Learning
- OCR (Optical Character Recognition)
- Data Analytics & Visualization
- User Authentication & Security
- Software Engineering & Clean Architecture
- Model Training, Evaluation & Deployment

---

## Author

BCA 5th Semester – Artificial Intelligence Major Project

---

## License

This project is created for educational purposes.
