"""
Database module – SQLAlchemy ORM models and session management.
Tables: Users, Expenses, Bills, Predictions, Budgets
"""

import os
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime,
    ForeignKey, Text, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "expense.db")

os.makedirs(DB_DIR, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    """Registered application user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")


class Expense(Base):
    """Individual expense transaction."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    payment_mode = Column(String(30), default="Cash")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="expenses")


class Bill(Base):
    """OCR-scanned bill record."""

    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_name = Column(String(150))
    bill_date = Column(Date)
    total_amount = Column(Float)
    items = Column(Text)
    image_path = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bills")


class Prediction(Base):
    """Stored ML spending prediction."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_amount = Column(Float, nullable=False)
    model_name = Column(String(50))
    accuracy = Column(Float)
    prediction_month = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class Budget(Base):
    """Monthly budget setting per user."""

    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="budgets")


def init_db():
    """Create all tables if they do not exist."""
    Base.metadata.create_all(engine)


def get_session():
    """Return a new database session."""
    return SessionLocal()
