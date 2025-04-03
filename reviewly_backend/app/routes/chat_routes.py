from flask_restx import Namespace, Resource, fields
from app.services.chat_service_v2 import ChatService
from flask import Response
from app.services.chat_session_manager import chat_session_manager

api = Namespace('chat', description='Chat related operations')


query_payload = api.model('QueryPayload', {
    'prompt': fields.String(required=True, description='The question or prompt to be answered'),
    'product_id': fields.String(required=True, description='The id of the specific product if we are in the product details page'),
    'model': fields.String(required=False, description='The model to use for the response', default="openai/gpt-4o-mini"),
    'session_id': fields.String(required=False, description='Session ID for continuous conversation')
})

chat_service_temp = ChatService(1)

@api.route('/query')
class GeneralQuery(Resource):
    @api.expect(query_payload)
    
    def post(self):
        data = api.payload
        question = data.get('prompt')
        product_id = data.get('product_id')
        model = data.get('model', "openai/gpt-4o-mini")
        session_id = data.get('session_id')

        if not session_id:
            session_id = chat_session_manager.create_session()

        chat_service = chat_session_manager.get_session(session_id)
        if not chat_service:
            return {"error": "Invalid session ID"}, 400
        

        if not question:
            return {"error": "No question provided"}, 400

        try:
            return Response(
                self.generate_stream(chat_service_temp, question, product_id, model),
                content_type='text/plain;charset=utf-8',
                status=200,
                headers={'X-Session-ID': session_id}  
            )
        except Exception as e:
            return {"error": str(e)}, 500

    def generate_stream(self, chat_service, question, product_id=None, model=None):
        """Genera el streaming de respuestas conforme se reciben."""
        try:
            for response_text in chat_service_temp.ask_question(
                prompt=question, 
                product_id=product_id,
                model=model
            ):
                yield response_text
        except Exception as e:
            yield f"Error en el streaming: {str(e)}\n"
