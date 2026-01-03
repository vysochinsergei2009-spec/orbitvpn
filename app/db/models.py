from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime, Numeric, Float, Text, CHAR, ARRAY, JSON
)
from .db import Base
from datetime import datetime

class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, index=True)
    name = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    vless_link = Column(String)
    username = Column(String)
    deleted = Column(Boolean, default=False)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    method = Column(String)
    amount = Column(Numeric)
    currency = Column(String)
    status = Column(String)
    comment = Column(Text)
    tx_hash = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    expected_crypto_amount = Column(Numeric, nullable=True)
    extra_data = Column(JSON, nullable=True)

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(BigInteger, primary_key=True)
    inviter_id = Column(BigInteger)
    invited_id = Column(BigInteger)
    invite_code = Column(Text)
    created_at = Column(DateTime)
    reward_given = Column(Boolean)
    reward_amount = Column(Float)
    note = Column(Text)

class TonTransaction(Base):
    __tablename__ = "ton_transactions"
    tx_hash = Column(Text, primary_key=True)
    amount = Column(Numeric)
    comment = Column(Text)
    sender = Column(String)
    created_at = Column(DateTime)
    processed_at = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = "users"
    tg_id = Column(BigInteger, primary_key=True)
    balance = Column(Numeric, default=0)
    subscription_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    username = Column(Text)
    lang = Column(String, default="ru")
    configs = Column(Integer, default=0)
    referrer_id = Column(BigInteger)
    first_buy = Column(Boolean, default=True)
    notifications = Column(Boolean, default=True)