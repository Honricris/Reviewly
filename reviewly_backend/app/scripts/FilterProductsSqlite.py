import json
import requests
import sqlite3

# Configuración de archivos y API
jsonl_file = "/home/carlos/Escritorio/Cuarto_Carrera/TFG/bbdd/Clothes/meta_Clothing_Shoes_and_Jewelry.jsonl"
reviews_file = "/home/carlos/Escritorio/Cuarto_Carrera/TFG/bbdd/Clothes/Clothing_Shoes_and_Jewelry.jsonl"
products_api_url = "http://127.0.0.1:5000/api/v0/products"
reviews_api_url = "http://localhost:5000/api/v0/reviews"
db_path = "/home/carlos/Escritorio/Cuarto_Carrera/TFG/bbdd/Videogames/reviews.db"


main_category = input("Introduce la categoría que se aplicará a todos los productos: ")


def create_reviews_table(db_path):
    """Crea la tabla de reseñas en la base de datos SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            parent_asin TEXT,
            review_data TEXT
        )
    ''')
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
        print("Rechazado: menos de 5 reseñas.")
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
    """Construye un índice de reseñas en una base de datos SQLite."""
    print(f"Construyendo índice de reseñas desde {reviews_file}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        with open(reviews_file, "r", encoding="utf-8") as file:
            count = 0
            for line in file:
                try:
                    review = json.loads(line.strip())
                    parent_asin = review.get("parent_asin") or review.get("asin")
                    review_id = review.get(str(count))  
                    review_data = json.dumps(review)
                    
                    cursor.execute('''
                        INSERT INTO reviews (review_id, parent_asin, review_data)
                        VALUES (?, ?, ?)
                    ''', (review_id, parent_asin, review_data))
                    
                    count += 1
                    print(count)
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

def process_product(product, db_path):
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
        print(f"Producto {parent_asin} aprobado y será guardado.")
        
        cursor.execute('''
            SELECT review_data FROM reviews WHERE parent_asin = ?
        ''', (parent_asin,))
        reviews = [json.loads(row[0]) for row in cursor.fetchall()]
        
        conn.close()
        return product, reviews
    
    print(f"Producto {parent_asin} rechazado.")
    conn.close()
    return None, []

def send_product_to_api(product, api_url):
    """Envía un producto a la API y devuelve True si se insertó correctamente, False si ya existía."""
    try:
        response = requests.post(api_url, json=product)
        if response.status_code == 201:
            print(f"Producto {product['parent_asin']} insertado correctamente.")
            return True
        elif response.status_code == 409:
            print(f"El producto {product['parent_asin']} ya existe en la base de datos.")
            return False
        else:
            print(f"Error al enviar el producto {product['parent_asin']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Ocurrió un error al enviar el producto {product['parent_asin']} a la API: {e}")
        return False

def send_reviews_to_api(reviews, api_url):
    """Envía las reviews a la API y devuelve una lista de review_id de las reseñas insertadas correctamente."""
    inserted_reviews = []
    success_count = 0 

    for review in reviews:
        try:
            response = requests.post(api_url, json=review)
            if response.status_code == 201:
                review_id = response.json().get('review_id')
                if review_id:
                    inserted_reviews.append(review_id)
                    success_count += 1
                    print(f"Review {review_id} insertada correctamente.")
                else:
                    print(f"Error: No se recibió un review_id en la respuesta para la review.")
            else:
                print(f"Error al insertar la review: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Ocurrió un error al enviar la review a la API: {e}")
    return success_count

def filter_and_send_products(jsonl_file, reviews_file, products_api_url, reviews_api_url, db_path):
    try:
        print("Iniciando el proceso de filtrado y envío...")
        create_reviews_table(db_path)  
        build_reviews_index(reviews_file, db_path)  
        
        with open(jsonl_file, "r", encoding="utf-8") as infile:
            print(f"Leyendo productos desde {jsonl_file}...")
            total_products = 0
            for line in infile:
                try:
                    product = json.loads(line.strip())
                    product_result, reviews = process_product(product, db_path)
                    if product_result:
                        if send_product_to_api(product_result, products_api_url):
                            parent_asin = product_result.get("parent_asin")
                            if reviews:
                                inserted_reviews = send_reviews_to_api(reviews, reviews_api_url)
                                print(f"Se insertaron {inserted_reviews} reviews para el producto {parent_asin}.")
                            else:
                                print(f"No se encontraron reviews para el producto {parent_asin}.")
                    total_products += 1
                except json.JSONDecodeError:
                    print("Error al decodificar un producto. Saltando...")
                    continue
            
            print(f"Proceso finalizado. Se procesaron {total_products} productos en total.")
    except FileNotFoundError:
        print(f"El archivo {jsonl_file} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo: {e}")

if __name__ == "__main__":
    filter_and_send_products(jsonl_file, reviews_file, products_api_url, reviews_api_url, db_path)