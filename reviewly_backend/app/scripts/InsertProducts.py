import json
import requests

# Configuración del archivo JSONL y API
jsonl_file = "/home/carlos/Escritorio/Cuarto Carrera/TFG/bbdd/Musical_instruments/meta_Musical_Instruments.jsonl"
api_url = "http://127.0.0.1:5000/api/v0/products"

def get_user_input():
    """Obtiene la configuración inicial del usuario."""
    while True:
        try:
            insert_all = input("¿Quieres insertar todos los productos del archivo? (s/n): ").strip().lower()
            if insert_all not in ['s', 'n']:
                raise ValueError("Por favor, introduce 's' para sí o 'n' para no.")
            insert_all = insert_all == 's'

            limit = 0
            if not insert_all:
                limit = int(input("¿Cuántos productos deseas insertar?: "))
                if limit <= 0:
                    raise ValueError("El número de productos debe ser mayor a cero.")
            
            main_category = input("Introduce la categoría principal para los productos: ").strip()
            if not main_category:
                raise ValueError("La categoría no puede estar vacía.")
            
            return insert_all, limit, main_category
        except ValueError as e:
            print(e)

def process_file(jsonl_file, insert_all, limit, main_category):
    """Procesa el archivo JSONL y devuelve los productos listos para enviar."""
    products_to_insert = []
    inserted_count = 0

    try:
        print(f"Abrindo el archivo: {jsonl_file}")
        with open(jsonl_file, "r", encoding="utf-8") as file:
            for line in file:
                if not insert_all and inserted_count >= limit:
                    print(f"Se alcanzó el límite de {limit} productos seleccionados.")
                    break

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar JSON: {line}")
                    continue

                product_data = {
                    "title": data.get("title", "Sin título"),
                    "main_category": main_category,
                    "average_rating": data.get("average_rating", 0.0),
                    "rating_number": data.get("rating_number", 0),
                    "features": data.get("features"),
                    "description": data.get("description"),
                    "price": data.get("price", 0.0),
                    "resume_review": data.get("resume_review"),
                    "images": data.get("images"),
                    "videos": data.get("videos"),
                    "store": data.get("store"),
                    "categories": data.get("categories"),
                    "details": data.get("details"),
                    "parent_asin": data.get("parent_asin"),
                    "asin": data.get("asin"),
                    "bought_together": data.get("bought_together"),
                    "amazon_link": f"https://www.amazon.com/dp/{data.get('asin', data.get('parent_asin'))}"
                }

                products_to_insert.append(product_data)
                inserted_count += 1

    except FileNotFoundError:
        print(f"El archivo {jsonl_file} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo: {e}")

    return products_to_insert

def send_to_api(products, api_url):
    """Envía los productos a la API en formato JSON."""
    try:
        print(f"Enviando {len(products)} productos a la API...")
        response = requests.post(api_url, json=products)
        if response.status_code == 201:
            print("Productos enviados exitosamente.")
            print(response.json())
        else:
            print(f"Error al enviar los productos: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ocurrió un error al enviar los datos a la API: {e}")

def main():
    # Obtener configuración del usuario
    insert_all, limit, main_category = get_user_input()

    # Procesar el archivo JSONL
    products_to_insert = process_file(jsonl_file, insert_all, limit, main_category)

    if products_to_insert:
        # Enviar productos procesados a la API
        send_to_api(products_to_insert, api_url)
    else:
        print("No se encontraron productos para insertar.")

if __name__ == "__main__":
    main()
