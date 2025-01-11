from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app import db


class AmazonUser(db.Model):
    __tablename__ = 'amazon_users'

    amazon_user_id = Column(String(255), primary_key=True) 
    name = Column(String(255))  
    created_at = Column(TIMESTAMP, default=func.now()) 
