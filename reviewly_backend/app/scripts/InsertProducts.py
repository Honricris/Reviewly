import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.review import Review
from app.models.product import Product

# Configuración de la base de datos
db_url = "postgresql://postgres:postgres@localhost:5432/Reviewly"
db_engine = create_engine(db_url)
Session = sessionmaker(bind=db_engine)
session = Session()

# Archivo JSONL y configuración del límite de inserción
jsonl_file = "/home/carlos/Escritorio/Cuarto Carrera/TFG/backend/Reviewly_Backend/app/scripts/meta_Appliances.jsonl"

# Variable global para controlar la inserción de todos los productos
insert_all_products = True  # Establece a True para insertar todos los productos, False para usar el límite

# Límite de inserción (solo se usa si insert_all_products es False)
limit = 30

inserted_count = 0

try:
    print(f"Abrindo el archivo: {jsonl_file}")
    with open(jsonl_file, "r", encoding="utf-8") as file:
        for line in file:
            print(f"Procesando línea: {line}")
            
            # Si no se insertan todos los productos, se verifica el límite
            if not insert_all_products and inserted_count >= limit:
                print(f"Se alcanzó el límite de {limit} productos insertados.")
                break

            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {line}")
                raise e

            # Verifica si el producto ya existe
            print(f"Verificando si el producto con parent_asin={data.get('parent_asin')} existe.")
            existing_product = session.query(Product).filter_by(parent_asin=data.get("parent_asin")).first()

            if existing_product:
                print(f"El producto con parent_asin={data['parent_asin']} ya existe. Se omite.")
                continue

            # Verifica si asin o parent_asin están presentes en los datos
            if "asin" not in data and "parent_asin" not in data:
                raise ValueError("Ni 'asin' ni 'parent_asin' están presentes en los datos del producto.")

            asin_value = data.get("asin", data.get("parent_asin"))

            amazon_link = f"https://www.amazon.com/dp/{asin_value}"

            main_category = data.get("main_category")
            if main_category is None:
                main_category = "Uncategorized" 

            # Crea un nuevo producto con todos los campos
            new_product = Product(
                title=data.get("title", "Sin título"),
                main_category=main_category,
                average_rating=data.get("average_rating", 0.0),
                rating_number=data.get("rating_number", 0),
                features=data.get("features"),
                description=data.get("description"),
                price=data.get("price", 0.0),
                resume_review=data.get("resume_review", None),
                images=data.get("images"),
                videos=data.get("videos"),
                store=data.get("store", None),
                categories=data.get("categories"),
                details=data.get("details"),
                parent_asin=data.get("asin"),
                bought_together=data.get("bought_together"),
                amazon_link=amazon_link,
                asin=asin_value
            )

            # Inserta el producto
            print(f"Ingresando el producto {data.get('title', 'sin título')}")
            session.add(new_product)
            inserted_count += 1

    # Confirma los cambios
    session.commit()
    print(f"Inserción completada: {inserted_count} productos insertados.")

except FileNotFoundError:
    print(f"El archivo {jsonl_file} no se encontró.")
except json.JSONDecodeError as e:
    print(f"Error al procesar el archivo JSONL: {e}")
except ValueError as ve:
    print(f"Error de valor: {ve}")
except Exception as e:
    session.rollback()
    print(f"Ocurrió un error: {e}")
    import traceback
    print("Detalles del error:")
    traceback.print_exc()  
finally:
    session.close()
