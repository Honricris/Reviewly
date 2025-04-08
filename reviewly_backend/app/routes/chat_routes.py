from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Response, request
from app.services.chat_service_v2 import ChatService
import traceback

api = Namespace('chat', description='Chat related operations')

query_payload = api.model('QueryPayload', {
    'prompt': fields.String(required=True, description='The question or prompt to be answered'),
    'product_id': fields.String(required=False, description='The id of the specific product if we are in the product details page'),
    'model': fields.String(required=False, description='The model to use for the response', default="openai/gpt-4o-mini")
})

@api.route('/query')
class GeneralQuery(Resource):
    @jwt_required()
    @api.expect(query_payload)
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        question = data.get('prompt')
        product_id = data.get('product_id')
        model = data.get('model', "openai/gpt-4o-mini")

        if not question:
            return {"error": "No question provided"}, 400

        chat_service = ChatService.get_instance(current_user_id)

        try:
            return Response(
                self.generate_stream(chat_service, question, product_id, model),
                content_type='text/plain;charset=utf-8',
                status=200
            )
        except Exception as e:
            print(traceback.format_exc())
            return {"error": str(e)}, 500

    def generate_stream(self, chat_service, question, product_id=None, model=None):
        """Genera el streaming de respuestas conforme se reciben."""
        try:
            for response_text in chat_service.ask_question(
                prompt=question, 
                product_id=product_id,
                model=model
            ):
                yield response_text
        except Exception as e:
            yield f"data: Error en el streaming: {str(e)}\n\n"

@api.route('/clear')
class ClearChat(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        ChatService.remove_instance(current_user_id)
        return {"status": "success", "message": "Chat session cleared"}, 200