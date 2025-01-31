import json
import requests

# Archivo JSON
json_file = "/home/carlos/Escritorio/Cuarto Carrera/TFG/bbdd/filtered_reviews.json"
api_url = "http://localhost:5000/api/v0/reviews"

# Contador de reseñas insertadas
reseñas_insertadas = 0

# Procesamiento de reseñas del archivo
try:
    print(f"Abriendo archivo JSON: {json_file}")
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)  # Carga todo el JSON como una lista

        for review in data:
            try:
                response = requests.post(api_url, json=review)  # Enviar como lista si el backend espera una
                if response.status_code == 404:
                    continue
                elif response.status_code == 201:
                    reseñas_insertadas += 1
                    print("Reseña procesada correctamente.")
                else:
                    print(f"Error al procesar reseña: {response.status_code} - {response.json()}")
            except requests.RequestException as e:
                print(f"Error en la petición al backend: {e}")

    print(f"Proceso finalizado. Reseñas insertadas: {reseñas_insertadas}")
except FileNotFoundError as e:
    print(f"El archivo {json_file} no se encontró: {e}")
except json.JSONDecodeError as e:
    print(f"Error al procesar el archivo JSON: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
