from flask_restx import Namespace, Resource, fields

from app.services.review_service import (
    create_review_for_product, delete_review, update_review
)

api = Namespace('reviews', description='Review related operations')


image_model = api.model('Image', {
    'small_image_url': fields.String(description='URL de la imagen pequeña', example="https://images-na.ssl-images-amazon.com/images/I/61gGVCuJyHL._SL256_.jpg"),
    'medium_image_url': fields.String(description='URL de la imagen mediana', example="https://images-na.ssl-images-amazon.com/images/I/61gGVCuJyHL._SL800_.jpg"),
    'large_image_url': fields.String(description='URL de la imagen grande', example="https://images-na.ssl-images-amazon.com/images/I/61gGVCuJyHL.jpg"),
    'attachment_type': fields.String(description='Tipo de adjunto', example="IMAGE")
})


review_model = api.model('Review', {
    'review_id': fields.Integer(description='ID de la reseña', example=1),
    'amazon_user_id': fields.String(description='ID del usuario en Amazon', example="user123"),
    'product_id': fields.Integer(description='ID del producto', example=101),
    'title': fields.String(description='Título de la reseña', example="Gran producto"),
    'text': fields.String(description='Texto de la reseña', example="Este producto superó mis expectativas..."),
    'rating': fields.Float(description='Calificación de la reseña', example=4.5),
    'images': fields.List(fields.Nested(image_model), description='Lista de imágenes con sus URLs y tipo de adjunto', example=[
        {
            "small_image_url": "https://images-na.ssl-images-amazon.com/images/I/61gGVCuJyHL._SL256_.jpg",
            "medium_image_url": "https://images-na.ssl-images-amazon.com/images/I/61gGVCuJyHL._SL800_.jpg",
            "large_image_url": "https://images-na.ssl-images-amazon.com/images/I/61gGVCuJyHL.jpg",
            "attachment_type": "IMAGE"
        },
        {
            "small_image_url": "https://images-na.ssl-images-amazon.com/images/I/61k6m6MmOpL._SL256_.jpg",
            "medium_image_url": "https://images-na.ssl-images-amazon.com/images/I/61k6m6MmOpL._SL800_.jpg",
            "large_image_url": "https://images-na.ssl-images-amazon.com/images/I/61k6m6MmOpL.jpg",
            "attachment_type": "IMAGE"
        }
    ]),   
    'sentiment': fields.String(description='Sentimiento de la reseña', example="positivo"),
    'helpful_vote': fields.Integer(description='Número de votos útiles', example=10),
    'verified_purchase': fields.Boolean(description='Compra verificada', example=True),
    'timestamp': fields.Integer(description='Fecha y hora de la reseña', example=1474996253000),
    'asin': fields.String(description='ASIN del producto', example="B08R29V9FQ"),
    'parent_asin': fields.String(description='Parent ASIN if any', example="B08J6F174Z")

})

@api.route('/')
class Reviews(Resource):
    @api.expect(review_model, validate=True)
    def post(self):
        """
        Crear una reseña basada en el parent_asin.
        """
        data = api.payload
     
        response, status_code = create_review_for_product(data)
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