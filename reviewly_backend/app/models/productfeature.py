from app import db
from sqlalchemy.types import UserDefinedType

class Vector(UserDefinedType):
    """
    Tipo personalizado para manejar vectores en PostgreSQL usando PGVector.
    """
    def get_col_spec(self):
        return "vector(1024)"


class ProductFeature(db.Model):
    __tablename__ = 'product_features'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)
    feature = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector, nullable=True)

    # Relación con Product
    product = db.relationship("Product", back_populates="features_list")

    def __repr__(self):
        return f"<ProductFeature {self.feature[:30]}...>"
