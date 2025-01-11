from app import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy.orm import relationship

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(1000), nullable=False)
    main_category = db.Column(db.String(255), nullable=False)
    average_rating = db.Column(db.Float, nullable=True, default=0.0)
    rating_number = db.Column(db.Integer, nullable=False, default=0)
    features = db.Column(JSONB, nullable=True)
    description = db.Column(JSONB, nullable=True)
    price = db.Column(db.Float, nullable=True, default=0.0)
    resume_review = db.Column(db.String(255), nullable=True)
    images = db.Column(JSONB, nullable=True)
    videos = db.Column(JSONB, nullable=True)
    store = db.Column(db.String(255), nullable=True)
    categories = db.Column(JSONB, nullable=True)
    details = db.Column(JSONB, nullable=True)
    parent_asin = db.Column(db.String(255), nullable=True)
    asin = db.Column(db.String(255), nullable=True)
    bought_together = db.Column(JSONB, nullable=True)
    amazon_link = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    #Relacion con reviews 
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        db.CheckConstraint('average_rating >= 0 AND average_rating <= 5', name='check_average_rating'),
        db.CheckConstraint('rating_number >= 0', name='check_rating_number'),
        db.CheckConstraint('price >= 0', name='check_price'),
    )


    def generate_amazon_link(self):
        # Si 'asin' está disponible, se usa ese valor; de lo contrario, usa 'parent_asin'.
        asin_to_use = self.asin if self.asin else self.parent_asin
        if asin_to_use:
            self.amazon_link = f"https://www.amazon.com/dp/{asin_to_use}"
            
    def __repr__(self):
        return f"<Product {self.title}>"
