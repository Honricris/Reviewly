from flask_restx import Namespace, Resource, fields
from app.services.chat_service import EdenAIChatService
from app.services.review_service import get_reviews_by_embedding
from flask import Response

api = Namespace('chat', description='Chat related operations')
eden_chat_service = EdenAIChatService()

# Definir el modelo de la solicitud (payload) para la ruta '/query' y '/product'
query_payload = api.model('QueryPayload', {
    'prompt': fields.String(required=True, description='The question or prompt to be answered')
})

@api.route('/query')
class GeneralQuery(Resource):
    @api.expect(query_payload)
    def post(self):
        data = api.payload
        question = data.get('prompt')

        if not question:
            return {"error": "No question provided"}, 400

        try:
            return Response(self.generate_stream(question), content_type='text/plain;charset=utf-8', status=200)
        except Exception as e:
            return {"error": str(e)}, 500

    def generate_stream(self, question):
        """Genera el streaming de respuestas conforme se reciben."""
        try:
            for response_text in eden_chat_service.ask_general_question_streaming(question):
                yield response_text
        except Exception as e:
            yield f"Error en el streaming: {str(e)}\n"



@api.route('/product/<int:product_id>')
class ProductQuery(Resource):
    @api.expect(query_payload)  
    def post(self, product_id):
        data = api.payload
        question = data.get('prompt')

        if not question:
            return {"error": "No question provided"}, 400
        
        reviews = get_reviews_by_embedding(question, product_id)

        if not reviews:
            return {"error": "No reviews found for the product"}, 404

        reviews_text = [review.text for review in reviews]
        answer = eden_chat_service.ask_based_on_reviews(reviews_text, question)
        review_ids = [review.review_id for review in reviews]

        return {
            "answer": answer,
            "reviews": review_ids
        }
