import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.review import Review
from app.models.product import Product
from app.models.amazonuser import AmazonUser
from sentence_transformers import SentenceTransformer
import os

# Configuración de conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada en el entorno.")
print(f"Conectando a la base de datos en: {DATABASE_URL}")

# Crear el motor y la fábrica de sesiones de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cargar el modelo de embeddings
model = SentenceTransformer("blevlabs/stella_en_v5", trust_remote_code=True)
print("Modelo de embeddings cargado.")

def update_embeddings(product_id):
    """
    Genera y actualiza los embeddings para todas las reseñas de un producto específico sin procesar.
    """
    session = SessionLocal() 
    print(f"Abriendo sesión de base de datos para el producto ID: {product_id}")

    try:
        # Obtener todas las reseñas del producto específico sin embedding
        reviews = session.query(Review).filter(
            Review.product_id == product_id,  # Filtrar por product_id
            Review.embedding.is_(None)  # Filtrar por reseñas sin embedding
        ).all()
        print(f"Total de reseñas pendientes de procesar: {len(reviews)}")

        if not reviews:
            print(f"No hay reseñas pendientes de procesar para el producto {product_id}.")
            return

        # Generar embedding para cada reseña de forma secuencial
        for review in reviews:
            sentence = review.text
            print(f"Generando embedding para reseña ID: {review.review_id}")

            # Generar embedding para la reseña
            embedding = model.encode([sentence])[0]  # Obtén el embedding para esta reseña

            # Actualizar la reseña con el embedding generado
            review.embedding = embedding.tolist()

            # Guardar los cambios en la base de datos
            session.commit()
            print(f"Embedding guardado para la reseña ID: {review.review_id}")

        # Realizar una consulta para comprobar que no hay reseñas con embedding NULL
        remaining_reviews = session.query(Review).filter(
            Review.product_id == product_id,
            Review.embedding.is_(None)  # Verifica si hay reseñas sin embedding
        ).all()

        if not remaining_reviews:
            print(f"Todos los embeddings han sido generados y guardados para el producto {product_id}.")
        else:
            print(f"¡Error! Hay reseñas sin embedding en el producto {product_id}.")

    except Exception as e:
        print(f"Error al generar embeddings: {e}")
        session.rollback() 
    finally:
        session.close() 
        print("Sesión cerrada.")


# Ejemplo de llamada de la función. python3 -m app.scripts.generate_embeddings 39706
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera embeddings para las reseñas de un producto específico.")
    parser.add_argument("product_id", type=int, help="ID del producto para el que generar embeddings.")
    args = parser.parse_args()

    print(f"Generando embeddings para el producto ID: {args.product_id}")
    
    update_embeddings(args.product_id)
