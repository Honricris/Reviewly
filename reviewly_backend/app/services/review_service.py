from app.models.review import Review
from app.models.product import Product
from datetime import datetime
from app.models.amazonuser import AmazonUser
from app.utils.model_loader import get_model

from app import db
from sqlalchemy.exc import  IntegrityError
from sqlalchemy import text

model = get_model()

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
        
        # Convertir rating a float para evitar problemas con Decimal
        reviews_dict = []
        for review in reviews:
            review_dict = review.to_dict()
            # Asegurarse de que el rating es un float
            review_dict['rating'] = float(review_dict['rating'])
            reviews_dict.append(review_dict)

        return reviews_dict, total_reviews 
    except Exception as e:
        print(f"Error fetching reviews for product {product_id}: {e}")
        return [], 0
    

def create_review_for_product(data: dict) -> tuple:
    """
    Crea una única reseña para un producto asociado a su parent_asin.

    Args:
        data (dict): Datos de la reseña.

    Returns:
        tuple: Respuesta en formato JSON y el código de estado HTTP.
    """

    # Buscar el producto usando el parent_asin
    parent_asin = data.get('parent_asin') or data.get('asin')
    print(f"parent_asin obtenido: {parent_asin}")
    
    if not parent_asin:
        return {"error": "No se encontró parent_asin en los datos de la reseña"}, 400

    product = Product.query.filter_by(parent_asin=parent_asin).first()
    if not product:
        print(f"Producto con parent_asin '{parent_asin}' no encontrado")
        return {"error": f"Producto con parent_asin '{parent_asin}' no encontrado"}, 404

    # Verificar si el usuario existe, si no, crearlo
    amazon_user = AmazonUser.query.filter_by(amazon_user_id=data['user_id']).first()
    print(f"Usuario encontrado: {amazon_user}")
    if not amazon_user:
        print(f"Usuario con amazon_user_id '{data['user_id']}' no encontrado. Creando usuario...")
        amazon_user = AmazonUser(
            amazon_user_id=data['user_id'],
            name=None  
        )
        try:
            db.session.add(amazon_user)
            db.session.commit()
            print(f"Usuario con amazon_user_id '{data['user_id']}' creado")
        except IntegrityError:
            db.session.rollback()
            amazon_user = AmazonUser.query.filter_by(amazon_user_id=data['user_id']).first()
            print(f"Error de integridad, usuario ya existe: {amazon_user}")

    # Procesar el timestamp
    try:
        print(f"Valor de timestamp antes de validación: {data.get('timestamp')}")
        if isinstance(data['timestamp'], int):
            timestamp = str(datetime.utcfromtimestamp(data['timestamp'] / 1000).isoformat())
            print(f"Timestamp convertido: {timestamp}")
        else:
            print(f"Timestamp no es un número válido: {data['timestamp']}")
            return {"error": "El timestamp debe ser un valor numérico en milisegundos."}, 400
    except Exception as e:
        print(f"Error al procesar el timestamp: {e}")
        return {"error": "Error procesando el timestamp"}, 400

    # Crear la reseña
    print(f"Creando reseña para producto con parent_asin '{parent_asin}'")
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
        parent_asin=parent_asin,
        asin=data.get('asin', product.asin),
        product_id=product.product_id
    )

    # Generar el embedding para la reseña
    try:
        print("Generando embedding para la reseña")
        review_embedding = model.encode([data['text']]).tolist()[0]
        review.embedding = review_embedding
    except Exception as e:
        print(f"Error generando el embedding: {e}")
        return {"error": "Error generando el embedding para la reseña"}, 500

    # Guardar la reseña en la base de datos
    try:
        print(f"Guardando reseña en la base de datos para producto con parent_asin '{parent_asin}'")
        db.session.add(review)
        db.session.commit()
        print(f"Reseña guardada: {review.to_dict()}")
        return review.to_dict(), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error guardando reseña: {e}")
        return {"error": str(e)}, 500




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