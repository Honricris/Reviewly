from flask import Blueprint, request, jsonify
from app.services.chat_service import EdenAIChatService
from app.services.review_service import (
    get_reviews_by_embedding
)
bp = Blueprint('chat_routes', __name__)
eden_chat_service = EdenAIChatService()

# Query general al chatbot
@bp.route('/chat/query', methods=['POST'])
def ask_general():
    data = request.get_json()
    question = data.get('prompt')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = eden_chat_service.ask_general_question(question)

    if answer == 'No response from Eden AI':
        return jsonify({"error": "Internal server error, no response from Eden AI"}), 500
    
    return jsonify({"answer": answer})

# Endpoint para preguntar por carácteristicas de Productos.
# Devuelve la respueste y las reviews en las que se ha basado para darla.
@bp.route('/chat/product/<product_id>', methods=['POST'])
def ask_product(product_id):
    data = request.get_json()
    print("Received JSON data:", data) 
    question = data.get('prompt')
    print("Extracted question:", question) 
    if not question:
        return jsonify({"error": "No question provided"}), 400
   
    reviews = get_reviews_by_embedding(question , product_id)

    if not reviews:
        return jsonify({"error": "No reviews found for the product"}), 404

    reviews_text = [review.text for review in reviews]

    answer = eden_chat_service.ask_based_on_reviews(reviews_text, question)

    review_ids = [review.review_id for review in reviews]

    return jsonify({
        "answer": answer,
        "reviews": review_ids 
    })