from flask import Blueprint, jsonify, request
from app.services.review_service import (
    create_reviews_for_product,
    delete_review,
    update_review
)

bp = Blueprint('review_routes', __name__)

# Crear las reseñas
@bp.route('/reviews/<int:product_id>', methods=['POST'])
def post_reviews(product_id):
    """
    Endpoint para crear múltiples reseñas para un producto específico.
    """
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of reviews"}), 400

    response, status_code = create_reviews_for_product(product_id, data)
    return jsonify(response), status_code


# Ruta para eliminar una reseña
@bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review_route(review_id):
    """Eliminar una reseña existente por su ID."""
    review = delete_review(review_id)

    if not review:
        return jsonify({"error": "Review not found"}), 404
    
    return jsonify({"message": "Review deleted successfully"}), 200

# Ruta para actualizar una reseña
@bp.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review_route(review_id):
    """Actualizar una reseña existente por su ID."""
    data = request.get_json()
    
    updated_review = update_review(review_id, data)

    if not updated_review:
        return jsonify({"error": "Review not found"}), 404

    return jsonify(updated_review), 200