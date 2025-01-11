from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, ForeignKey, JSON, TIMESTAMP, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import UserDefinedType
from app import db

class Vector(UserDefinedType):
    """
    Tipo personalizado para manejar vectores en PostgreSQL usando PGVector.
    """
    def get_col_spec(self):
        return "vector(8192)"

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True, autoincrement=True)  
    amazon_user_id = Column(String(255), ForeignKey('amazon_users.amazon_user_id', ondelete='CASCADE'), nullable=False)  
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)  
    title = Column(String(255))  
    text = Column(Text)  
    rating = Column(Numeric(2, 1), nullable=False)  
    images = Column(JSON) 
    sentiment = Column(String(50), default='neutral') 
    helpful_vote = Column(Integer, default=0)  
    verified_purchase = Column(Boolean, default=False)  
    timestamp = Column(TIMESTAMP, default=func.now()) 
    created_at = Column(TIMESTAMP, default=func.now())
    asin = Column(String(255))  
    parent_asin = Column(String(255)) 
    embedding = Column(Vector, nullable=True)  # Campo para almacenar embeddings como vector(8192)

    # Relación con la tabla de productos
    product = relationship("Product", back_populates="reviews", lazy=True)

    def __repr__(self):
        return f"<Review(review_id={self.review_id}, product_id={self.product_id}, rating={self.rating})>"

    def to_dict(self):
        """
        Convierte la reseña en un diccionario serializable.
        """
        return {
            "review_id": self.review_id,
            "amazon_user_id": self.amazon_user_id,
            "product_id": self.product_id,
            "title": self.title,
            "text": self.text,
            "rating": self.rating,
            "images": self.images,
            "sentiment": self.sentiment,
            "helpful_vote": self.helpful_vote,
            "verified_purchase": self.verified_purchase,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "asin": self.asin,  
            "parent_asin": self.parent_asin,  
        }
