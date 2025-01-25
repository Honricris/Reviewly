from flask_restx import Namespace, Resource, fields

from app.services.review_service import (
    create_reviews_for_product, delete_review, update_review
)

api = Namespace('reviews', description='Review related operations')

review_model = api.model('Review', {
    'review_id': fields.Integer(description='ID de la reseña', example=1),
    'amazon_user_id': fields.String(description='ID del usuario en Amazon', example="user123"),
    'product_id': fields.Integer(description='ID del producto', example=101),
    'title': fields.String(description='Título de la reseña', example="Gran producto"),
    'text': fields.String(description='Texto de la reseña', example="Este producto superó mis expectativas..."),
    'rating': fields.Float(description='Calificación de la reseña', example=4.5),
    'images': fields.List(fields.String, description='Imágenes de la reseña', example=["image1.jpg", "image2.jpg"]),
    'sentiment': fields.String(description='Sentimiento de la reseña', example="positivo"),
    'helpful_vote': fields.Integer(description='Número de votos útiles', example=10),
    'verified_purchase': fields.Boolean(description='Compra verificada', example=True),
    'timestamp': fields.DateTime(description='Fecha y hora de la reseña', example="2023-12-01T12:00:00Z"),
    'asin': fields.String(description='ASIN del producto', example="B08R29V9FQ"),
    'parent_asin': fields.String(description='Parent ASIN if any', example="B08J6F174Z")

})

# Ruta para crear reseñas para un producto
@api.route('/<int:product_id>')
class Reviews(Resource):
    @api.expect(review_model, validate=True)
    def post(self, product_id):
        """
        Crear reseñas para un producto
        """
        data = api.payload
        if not isinstance(data, list):
            return {"error": "Se esperaba una lista de reseñas"}, 400

        response, status_code = create_reviews_for_product(product_id, data)
        return response, status_code

# Ruta para eliminar una reseña
@api.route('/<int:review_id>')
class Review(Resource):
    def delete(self, review_id):
        """
        Eliminar una reseña
        """
        review = delete_review(review_id)
        if not review:
            return {"error": "Reseña no encontrada"}, 404
        return {"message": "Reseña eliminada correctamente"}, 200

    @api.expect(review_model, validate=True)
    def put(self, review_id):
        """
        Actualizar una reseña
        """
        data = api.payload
        updated_review = update_review(review_id, data)
        if not updated_review:
            return {"error": "Reseña no encontrada"}, 404
        return updated_review, 200