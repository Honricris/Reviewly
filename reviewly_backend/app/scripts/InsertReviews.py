import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.review import Review
from app.models.product import Product
from app.models.amazonuser import AmazonUser
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import create_app
from app import db

# Configuración global: insertará todas las reseñas del archivo si es True
INSERT_ALL_REVIEWS = True

# Crear la aplicación Flask y configurar el contexto
app = create_app()

# Archivo JSONL
jsonl_file = "/home/carlos/Escritorio/Cuarto Carrera/TFG/bbdd/Appliances.jsonl"

def create_reviews_for_product(product_id: int, reviews: list) -> tuple:
    """
    Crea múltiples reseñas para un producto específico.

    Args:
        product_id (int): ID del producto al que se añadirán las reseñas.
        reviews (list): Lista de datos de reseñas.

    Returns:
        tuple: Respuesta en formato JSON y el código de estado HTTP.
    """
    with app.app_context(): 
        print(f"Buscando producto con ID: {product_id}")
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            print(f"Producto no encontrado para product_id: {product_id}")
            return {"error": "Product not found for the given product_id"}, 404

        created_reviews = []

        for data in reviews:
            print(f"Procesando reseña para usuario: {data['user_id']}")

            amazon_user = AmazonUser.query.filter_by(amazon_user_id=data['user_id']).first()
            if not amazon_user:
                print(f"Usuario Amazon no encontrado, creando nuevo usuario con ID: {data['user_id']}")
                amazon_user = AmazonUser(
                    amazon_user_id=data['user_id'],
                    name=None
                )
                try:
                    db.session.add(amazon_user)
                    db.session.commit()
                    print(f"Usuario Amazon creado con éxito: {data['user_id']}")
                except IntegrityError as e:
                    db.session.rollback()
                    print(f"Error al insertar usuario Amazon: {e}")
                    amazon_user = AmazonUser.query.filter_by(amazon_user_id=data['user_id']).first()

            try:
                timestamp = datetime.utcfromtimestamp(data['timestamp'] / 1000)
            except Exception as e:
                print(f"Error al convertir el timestamp: {e}")
                timestamp = None

            try:
                parent_asin = data.get('parent_asin') or data.get('asin')
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
                    asin=data.get('parent_asin', product.parent_asin),
                    product_id=product.product_id
                )

                db.session.add(review)
                db.session.commit()
                created_reviews.append(review.to_dict())
                print(f"Reseña creada con éxito para usuario: {data['user_id']}")
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error al guardar la reseña en la base de datos: {e}")
                return {"error": f"Error al insertar reseña: {str(e)}"}, 500
            except Exception as e:
                db.session.rollback()
                print(f"Error inesperado al guardar la reseña: {e}")
                return {"error": str(e)}, 500

        print(f"Total de reseñas creadas: {len(created_reviews)}")
        return created_reviews, 201

# Procesamiento de reseñas del archivo
inserted_count = 0

try:
    print(f"Abriendo archivo JSONL: {jsonl_file}")
    with open(jsonl_file, "r", encoding="utf-8") as file:
        for line in file:
            data = json.loads(line)

            asin = data.get('parent_asin')
            if not asin:
                print("No ASIN found in review data. Skipping.")
                continue

            with app.app_context():
                try:
                    print(f"Buscando producto con ASIN: {asin}")
                    product = db.session.query(Product).filter_by(asin=asin).first()
                    if not product:
                        print(f"Producto con ASIN {asin} no encontrado. Se omite.")
                        continue

                    created_reviews, status_code = create_reviews_for_product(product.product_id, [data])

                    if status_code == 201:
                        inserted_count += 1
                        print(f"Reseña insertada correctamente. Total insertadas: {inserted_count}")
                    else:
                        print(f"Error al insertar review: {status_code}")
                except Exception as e:
                    print(f"Error al procesar producto con ASIN {asin}: {e}")

    print(f"Inserción completada: {inserted_count} reseñas insertadas.")

except FileNotFoundError as e:
    print(f"El archivo {jsonl_file} no se encontró: {e}")
except json.JSONDecodeError as e:
    print(f"Error al procesar el archivo JSONL: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
