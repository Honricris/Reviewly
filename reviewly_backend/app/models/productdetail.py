from app import db
from sqlalchemy.orm import relationship
from sqlalchemy.types import UserDefinedType


class Vector(UserDefinedType):
    """
    Tipo personalizado para manejar vectores en PostgreSQL usando PGVector.
    """
    def get_col_spec(self):
        return "vector(1024)"


class ProductDetail(db.Model):
    __tablename__ = 'product_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    detail = db.Column(db.String(1500), nullable=False)
    detail_embedding = db.Column(Vector, nullable=True)

    product = relationship("Product", back_populates="details_list")

    def __repr__(self):
        return f"<ProductDetail {self.detail}>"
