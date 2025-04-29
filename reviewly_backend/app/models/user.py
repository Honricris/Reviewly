from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from app import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = Column(Integer, unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    role = Column(String(50), nullable=False, default="user")
    favorites = relationship('Product', secondary='user_favorites', backref='favorited_by')
    login_logs = relationship('LoginLog', backref='user', cascade='all, delete-orphan')  

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
)