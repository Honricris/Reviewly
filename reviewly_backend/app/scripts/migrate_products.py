from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import db
from app.models.product import Product
from app.models.productfeature import ProductFeature  # Importa el nuevo modelo
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

def migrate_features_to_product_features():
    """
    Migra las features de todos los productos a la tabla ProductFeature y genera embeddings.
    Si ocurre un error al procesar un producto, continúa con el siguiente.
    """
    session = SessionLocal()
    print("Abriendo sesión de base de datos para migrar todos los productos")

    try:
        # Obtener todos los productos
        products = session.query(Product).all()
        print(f"Total de productos encontrados: {len(products)}")

        if not products:
            print("No se encontraron productos para migrar.")
            return

        for product in products:
            if product.features:
                for feature_text in product.features:
                    
                    # Generar embedding para la feature
                    try:
                        embedding = model.encode([feature_text])[0]  

                        new_feature = ProductFeature(
                            product_id=product.product_id,
                            feature=feature_text,
                            embedding=embedding.tolist()
                        )
                        session.add(new_feature)
                        print(f"Feature migrada para producto ID: {product.product_id}")

                    except Exception as embed_error:
                        print(f"Error al generar embedding para producto ID: {product.product_id}, feature: {feature_text}")
                        print(f"Detalles del error: {embed_error}")
                        continue  

                try:
                    session.commit()
                    print(f"Migración completada para producto ID: {product.product_id}")
                except Exception as commit_error:
                    print(f"Error al guardar features para producto ID: {product.product_id}")
                    print(f"Detalles del error: {commit_error}")
                    session.rollback()

    except Exception as e:
        print(f"Error general durante la migración: {e}")
        session.rollback()
    finally:
        session.close()
        print("Sesión cerrada.")

if __name__ == "__main__":
    print("Iniciando migración de features y generación de embeddings para todos los productos")
    migrate_features_to_product_features()
