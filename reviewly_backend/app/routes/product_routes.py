from flask import Blueprint, jsonify, request
from app.services.product_service import (
    get_all_products, 
    get_product_by_id, 
    create_product, 
    update_product, 
    delete_product
)

from app.services.review_service import (
    get_reviews_by_product
)


bp = Blueprint('product_routes', __name__)

# Listar productos
@bp.route('/products', methods=['GET'])
def get_products():
    # Obtener los parámetros de la query string
    category = request.args.get('category')  # Filtrar por categoría
    limit = request.args.get('limit', type=int)  # Limitar el número de productos devueltos
    page = request.args.get('page', type=int)  # Limitar el número de productos devueltos

    products = get_all_products(category=category, limit=limit, page = page)
    
    return jsonify(products), 200

# Crear Productos
@bp.route('/products', methods=['POST'])
def post_product():
    data = request.get_json()
    product = create_product(data)
    return jsonify(product), 201

# Seleccionar un producto concreto
@bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = get_product_by_id(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

# Actualizar un producto
@bp.route('/products/<int:id>', methods=['PUT'])
def put_product(id):
    data = request.get_json()
    product = update_product(id, data)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

# Eliminar un producto
@bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product_route(id):
    success = delete_product(id)
    if not success:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted"}), 200

# Obtener reviews de un producto
@bp.route('/products/<int:id>/reviews', methods=['GET'])
def get_product_reviews(id):
    try:
        page = int(request.args.get('page', 1)) 
        per_page = 10  # Tamaño fijo de reviews por página
        offset = (page - 1) * per_page  # Calcular el offset basado en la página
        
        result = get_reviews_by_product(id, limit=per_page, offset=offset)
        print(f"Result from get_reviews_by_product: {result}")
        reviews, total_reviews = result

        if not reviews:
            return jsonify({
                "error": "No reviews found for this product.",
                "page": page,
                "per_page": per_page
            }), 404
        
        return jsonify({
            "reviews": reviews,
            "total_reviews": total_reviews,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_reviews + per_page - 1) // per_page
        }), 200
    except Exception as e:
        print(f"Error in get_product_reviews: {e}")
        return jsonify({"error": "An error occurred while fetching reviews."}), 500