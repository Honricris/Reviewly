import json

#Script para seleccionar las reviews que se relacionan con los productos que existen actualmente con la bbdd 
# Lista de valores de asin o parent_asin a buscar
asin_list = {
    "B01M4HO6RK", "B00508JFE4", "B000S5JGMU", "B00B2HLWZW", 
    "B0B89ZSYS7", "B00HXKFQLI", "B0891SBM1L", "B08K8V4JCY", 
    "B008CMVWOG", "B01HY530RS"
}


# Archivo de entrada y salida
input_file = "" 
output_file = "filtered_reviews.json"

# Leer el archivo línea por línea y filtrar las reseñas
filtered_reviews = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            review = json.loads(line.strip())
            if review.get("parent_asin") in asin_list or review.get("asin") in asin_list:
                filtered_reviews.append(review)
        except json.JSONDecodeError:
            continue 

# Guardar las reseñas filtradas en un nuevo archivo JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(filtered_reviews, f, indent=4)

print(f"Se han guardado {len(filtered_reviews)} reseñas en '{output_file}'")

