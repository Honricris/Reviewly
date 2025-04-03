from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = db.Column(Integer, unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    role = Column(String(50), nullable=False, default="user") 

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"