from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Float
from sqlalchemy.sql import func
from app import db

class UserQuery(db.Model):
    __tablename__ = 'user_queries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    query_text = Column(String(500), nullable=False)
    execution_time = Column(Float, nullable=True) 
    created_at = Column(TIMESTAMP, default=func.now())
    
    user = db.relationship('User', back_populates='queries') 
    
    def __repr__(self):
        return f"<UserQuery(user_id={self.user_id}, query='{self.query_text[:20]}...', execution_time={self.execution_time}s)>"