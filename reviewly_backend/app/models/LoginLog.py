from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app import db

class LoginLog(db.Model):
    __tablename__ = 'login_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ip_address = Column(String(45), nullable=False)
    login_at = Column(TIMESTAMP, nullable=False, default=func.now())

    def __repr__(self):
        return f"<LoginLog(id={self.id}, user_id={self.user_id}, ip_address={self.ip_address}, login_at={self.login_at})>"