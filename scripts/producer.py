import json
import sqlite3
from kafka import KafkaProducer
import time
import hashlib
import os

# Configuración de archivos y Kafka
jsonl_file = "/home/carlos/Escritorio/Cuarto_Carrera/TFG/Reviewly/data/meta_Electronics.jsonl"
reviews_file = "/home/carlos/Escritorio/Cuarto_Carrera/TFG/Reviewly/data/Electronics.jsonl"
db_path = "electronics.db"
tracking_file = "last_sent.json"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all'
)

main_category = input("Introduce la categoría que se aplicará a todos los productos: ")

def load_last_sent():
    """Carga el último parent_asin enviado desde el archivo de seguimiento."""
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading {tracking_file}, starting from beginning")
                return {'products': None, 'reviews': None}
    return {'products': None, 'reviews': None}

def save_last_sent(topic, parent_asin):
    """Guarda el último parent_asin enviado para el topic especificado."""
    last_sent = load_last_sent()
    last_sent[topic] = parent_asin
    with open(tracking_file, 'w', encoding='utf-8') as f:
        json.dump(last_sent, f, indent=2)

def create_reviews_table(db_path):
    """Crea la tabla de reseñas en la base de datos SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            parent_asin TEXT,
            file_offset INTEGER
        )
    ''')
    # Crear un índice en parent_asin para acelerar las consultas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_parent_asin ON reviews(parent_asin)')
    conn.commit()
    conn.close()

def apply_filters(product, review_count):
    """Aplica los filtros al producto."""
    print(f"Aplicando filtros a producto {product.get('parent_asin', 'Desconocido')}, número de reseñas: {review_count}")
    product["main_category"] = main_category
    if review_count < 5:
        print("Rechazado: menos de 5 reseñas.")
        return False
    if review_count > 50:
        print("Rechazado: más de 50 reseñas.")
        return False
    if not product.get("description"):
        print("Rechazado: sin descripción.")
        return False
    price = product.get("price")
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        print("Rechazado: precio inválido.")
        return False
    print("Producto aprobado.")
    return True

def build_reviews_index(reviews_file, db_path):
    """Construye un índice de reseñas en una base de datos SQLite con review_id, parent_asin y file_offset."""
    print(f"Construyendo índice de reseñas desde {reviews_file}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        with open(reviews_file, "r", encoding="utf-8") as file:
            count = 0
            file_offset = 0
            while True:
                line = file.readline()
                if not line:  
                    break
                try:
                    review = json.loads(line.strip())
                    parent_asin = review.get("parent_asin") or review.get("asin")
                    review_id = str(count)
                    
                    cursor.execute('''
                        INSERT INTO reviews (review_id, parent_asin, file_offset)
                        VALUES (?, ?, ?)
                    ''', (review_id, parent_asin, file_offset))
                    
                    count += 1
                    file_offset = file.tell()  
                    if count % 1000 == 0:
                        print(f"Procesadas {count} reseñas...")
                except json.JSONDecodeError:
                    print("Error al decodificar una reseña. Saltando...")
                    continue
        conn.commit()
        print(f"Índice de reseñas construido con {count} reseñas.")
    except FileNotFoundError:
        print(f"El archivo {reviews_file} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al construir el índice de reseñas: {e}")
    finally:
        conn.close()

def get_reviews_from_file(reviews_file, review_ids, file_offsets):
    """Lee las reseñas desde el archivo usando los offsets correspondientes."""
    reviews = []
    try:
        with open(reviews_file, "r", encoding="utf-8") as file:
            for review_id, offset in zip(review_ids, file_offsets):
                try:
                    file.seek(offset)
                    line = file.readline().strip()
                    review = json.loads(line)
                    reviews.append(review)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error al leer reseña {review_id} en offset {offset}: {e}")
                    continue
    except FileNotFoundError:
        print(f"El archivo {reviews_file} no se encontró.")
    return reviews

def process_product(product, db_path, reviews_file):
    """Procesa un producto y devuelve el producto y sus reseñas si pasa los filtros."""
    asin = product.get("parent_asin", "Desconocido")
    print(f"Procesando producto {asin}...")
    parent_asin = product.get("parent_asin") or asin
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM reviews WHERE parent_asin = ?
    ''', (parent_asin,))
    review_count = cursor.fetchone()[0]
    
    if apply_filters(product, review_count):
        print(f"Producto {parent_asin} aprobado y será enviado.")
        
        cursor.execute('''
            SELECT review_id, file_offset FROM reviews WHERE parent_asin = ?
        ''', (parent_asin,))
        results = cursor.fetchall()
        review_ids = [row[0] for row in results]
        file_offsets = [row[1] for row in results]
        
        conn.close()
        
        # Leer las reseñas desde el archivo usando los offsets
        reviews = get_reviews_from_file(reviews_file, review_ids, file_offsets)
        return product, reviews
    
    print(f"Producto {parent_asin} rechazado.")
    conn.close()
    return None, []

def transform_review(review):
    """Transforma una reseña al formato esperado."""
    return {
        'user_id': review.get('user_id', ''),
        'title': review.get('title', ''),
        'text': review.get('text', ''),
        'rating': review.get('rating', 0.0),
        'images': review.get('images', []),  
        'helpful_vote': review.get('helpful_vote', 0),
        'verified_purchase': review.get('verified_purchase', False),
        'timestamp': review.get('timestamp', 0),
        'asin': review.get('asin', ''),
        'parent_asin': review.get('parent_asin', '')
    }

def send_to_kafka(topic, record, parent_asin):
    """Envía un registro a un topic de Kafka y actualiza el archivo de seguimiento."""
    try:
        future = producer.send(topic, record)
        future.get(timeout=10)
        print(f"Enviado a {topic}: {parent_asin}")
        save_last_sent(topic, parent_asin)
        return True
    except Exception as e:
        print(f"Error al enviar a {topic}: {e}")
        return False

def filter_and_send_products(jsonl_file, reviews_file, db_path):
    try:
        print("Iniciando el proceso de filtrado y envío a Kafka...")
        
        if os.path.exists(db_path):
            print(f"La base de datos {db_path} ya existe. Saltando la creación de la tabla y el índice de reseñas...")
        else:
            print(f"La base de datos {db_path} no existe. Creando tabla e índice de reseñas...")
            create_reviews_table(db_path)
            build_reviews_index(reviews_file, db_path)
        

        last_sent = load_last_sent()
        last_parent_asin = last_sent.get('products')
        skip_mode = last_parent_asin is not None
        
        with open(jsonl_file, "r", encoding="utf-8") as infile:
            print(f"Leyendo productos desde {jsonl_file}...")
            total_products = 0
            processed_products = 0
            for line in infile:
                try:
                    processed_products += 1
                    print(f"\n--- Procesando línea {processed_products} del archivo ---")
                    
                    product = json.loads(line.strip())
                    parent_asin = product.get("parent_asin", hashlib.md5(product.get('title', '').encode()).hexdigest()[:10])
                    print(f"Producto actual: {parent_asin}, Último producto enviado: {last_parent_asin}")
                    
                    # Skip products until we pass the last sent parent_asin
                    if skip_mode:
                        print(f"Modo skip activado. Comparando {parent_asin} con {last_parent_asin}")
                        if parent_asin == last_parent_asin:
                            skip_mode = False
                            print(f"Encontrado último producto enviado. Continuando con nuevos productos...")
                        else:
                            print(f"Saltando producto {parent_asin}...")
                        continue
                    
                    print(f"Procesando producto {parent_asin}...")
                    product_result, reviews = process_product(product, db_path, reviews_file)
                    if product_result:
                        print(f"Producto {parent_asin} aprobado. Preparando para enviar...")
                        # Enviar producto a Kafka
                        if send_to_kafka('products', product_result, parent_asin):
                            print(f"Producto {parent_asin} enviado exitosamente.")
                            if reviews:
                                success_count = 0
                                for review in reviews:
                                    transformed_review = transform_review(review)
                                    if send_to_kafka('reviews', transformed_review, parent_asin):
                                        success_count += 1
                                print(f"Se enviaron {success_count} reviews para el producto {parent_asin}.")
                            else:
                                print(f"No se encontraron reviews para el producto {parent_asin}.")
                            print(f"Durmiendo durante 5 minutos hasta el siguiente envio ......")
                            time.sleep(300)
                        else:
                            print(f"Error al enviar producto {parent_asin} a Kafka.")
                    else:
                        print(f"Producto {parent_asin} no aprobado. Continuando con el siguiente producto...")
                    
                    total_products += 1

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar un producto. Saltando... Error: {e}")
                    continue
                except Exception as e:
                    print(f"Error inesperado procesando producto: {e}")
                    continue
            
            print(f"Proceso finalizado. Se procesaron {total_products} productos en total de {processed_products} líneas leídas.")
    except FileNotFoundError:
        print(f"El archivo {jsonl_file} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo: {e}")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    filter_and_send_products(jsonl_file, reviews_file, db_path)