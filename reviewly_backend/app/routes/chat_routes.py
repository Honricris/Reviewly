from flask_restx import Namespace, Resource, fields
from app.services.chat_service_v2 import ChatService
from flask import Response

api = Namespace('chat', description='Chat related operations')
chat_service = ChatService()

query_payload = api.model('QueryPayload', {
    'prompt': fields.String(required=True, description='The question or prompt to be answered'),
    'product_id': fields.String(required=True, description='The id of the specific product if we are in the product details page')

})

@api.route('/query')
class GeneralQuery(Resource):
    @api.expect(query_payload)
    def post(self):
        data = api.payload
        question = data.get('prompt')
        product_id = data.get('product_id')

        if not question:
            return {"error": "No question provided"}, 400

        try:
            return Response(self.generate_stream(question, product_id), content_type='text/plain;charset=utf-8', status=200)
        except Exception as e:
            return {"error": str(e)}, 500

    def generate_stream(self, question, product_id=None):
        """Genera el streaming de respuestas conforme se reciben."""
        try:
            for response_text in chat_service.ask_question(question, product_id):
                yield response_text
        except Exception as e:
            yield f"Error en el streaming: {str(e)}\n"
