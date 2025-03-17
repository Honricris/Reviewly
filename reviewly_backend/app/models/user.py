from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"