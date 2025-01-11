from app.models.review import Review
from app.models.product import Product
from datetime import datetime
from app.models.amazonuser import AmazonUser

from app import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("blevlabs/stella_en_v5", trust_remote_code=True)

def get_reviews_by_product(product_id, limit=10, offset=0):
    try:
        total_reviews = db.session.query(Review).filter_by(product_id=product_id).count()  
        reviews = (
            db.session.query(Review)
            .filter_by(product_id=product_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        print(f"Returning reviews: {reviews}, total_reviews: {total_reviews}")
        return [review.to_dict() for review in reviews], total_reviews 
    except Exception as e:
        print(f"Error fetching reviews for product {product_id}: {e}")
        return [], 0
    

def create_reviews_for_product(product_id: int, reviews: list) -> tuple:
    """
    Crea múltiples reseñas para un producto específico.

    Args:
        product_id (int): ID del producto al que se añadirán las reseñas.
        reviews (list): Lista de datos de reseñas.

    Returns:
        tuple: Respuesta en formato JSON y el código de estado HTTP.
    """
    # Buscar el producto en la base de datos
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return {"error": "Product not found for the given product_id"}, 404

    created_reviews = []

    for data in reviews:
        # Verificar si el usuario existe
        amazon_user = AmazonUser.query.filter_by(amazon_user_id=data['user_id']).first()
        if not amazon_user:
            amazon_user = AmazonUser(
                amazon_user_id=data['user_id'],
                name=None  
            )
            try:
                db.session.add(amazon_user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                amazon_user = AmazonUser.query.filter_by(amazon_user_id=data['user_id']).first()

        timestamp = datetime.utcfromtimestamp(data['timestamp'] / 1000)

        review = Review(
            amazon_user_id=data['user_id'],
            title=data['title'],
            text=data['text'],
            rating=data['rating'],
            images=data['images'],
            sentiment=data.get('sentiment', 'neutral'),
            helpful_vote=data.get('helpful_vote', 0),
            verified_purchase=data.get('verified_purchase', False),
            timestamp=timestamp,
            parent_asin=product.parent_asin, 
            asin=data.get('asin', product.parent_asin),
            product_id=product.product_id
        )

        # Guardar la reseña en la base de datos
        try:
            db.session.add(review)
            db.session.commit()
            created_reviews.append(review.to_dict())
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    return created_reviews, 201

def delete_review(review_id: int):
    """Elimina una reseña por su ID."""
    # Buscar la reseña por review_id
    review = Review.query.filter_by(review_id=review_id).first()
    
    if not review:
        return None  
    
    try:
        db.session.delete(review)
        db.session.commit()
        return review  
    
    except Exception as e:
        db.session.rollback() 
        raise e  
    


def update_review(review_id, data):
    """Actualiza todos los campos de una reseña existente."""
    review = Review.query.get(review_id)
    
    if not review:
        return None

    # Actualizar todos los campos con los datos proporcionados
    review.amazon_user_id = data['user_id']
    review.title = data['title']
    review.text = data['text']
    review.rating = data['rating']
    review.images = data['images']
    review.sentiment = data.get('sentiment', review.sentiment)
    review.helpful_vote = data.get('helpful_vote', review.helpful_vote)
    review.verified_purchase = data.get('verified_purchase', review.verified_purchase)
    review.timestamp = data.get('timestamp', review.timestamp)
    review.parent_asin = data['parent_asin']
    review.asin = data.get('asin', data['parent_asin'])
    review.product_id = data['product_id']

    # Guardar los cambios en la base de datos
    db.session.commit()

    return review.to_dict()

def get_reviews_by_embedding(query_text, product_id, top_k=3):
    """
    Busca las reseñas más cercanas a la pregunta del usuario usando el índice ivfflat
    y las reseñas asociadas a un producto específico.
    
    Args:
        query_text (str): El texto de la pregunta del usuario.
        product_id (int): El ID del producto para filtrar las reseñas.
        top_k (int): El número de reseñas más cercanas a devolver.
    
    Returns:
        list: Las reseñas más cercanas.
    """
    try:
        # Convertir el texto de la consulta en un embedding usando el modelo
        query_embedding = model.encode([query_text]).tolist()[0]
        
        # Convertir el embedding a un formato compatible con PostgreSQL (ARRAY)
        query_embedding_array = "[" + ",".join(map(str, query_embedding)) + "]"

        # Realizar la búsqueda de similitud utilizando el índice ivfflat
        result = db.session.query(Review).from_statement(
            text("""
            SELECT * FROM reviews
            WHERE product_id = :product_id
            ORDER BY embedding <=> :query_embedding
            LIMIT :top_k
            """)
        ).params(query_embedding=query_embedding_array, product_id=product_id, top_k=top_k).all()

        return result

    except Exception as e:
        print(f"Error while fetching closest reviews: {e}")
        return None