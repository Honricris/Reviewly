from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.services.user_service import UserService

api = Namespace('user', description='User related operations')

favorite_product_model = api.model('FavoriteProduct', {
    'product_id': fields.Integer(readonly=True),
    'title': fields.String(readonly=True),
    'price': fields.Float(readonly=True),
    'average_rating': fields.Float(readonly=True),
    'store': fields.String(readonly=True),
    'image': fields.String(attribute=lambda x: x.images[0] if x.images and len(x.images) > 0 else None)
})

product_id_payload = api.model('ProductIdPayload', {
    'product_id': fields.Integer(required=True, description='The ID of the product to add/remove from favorites')
})

@api.route('/favorites')
class UserFavorites(Resource):
    @jwt_required()
    def get(self):
        """Get list of user's favorite product IDs"""
        current_user_id = get_jwt_identity()
        favorite_ids, error = UserService.get_user_favorite_ids(current_user_id)  # Nuevo método
        
        if error:
            api.abort(404, error)
        return favorite_ids  

    @jwt_required()
    @api.expect(product_id_payload)
    def post(self):
        """Add a product to user's favorites"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            api.abort(400, "Product ID is required")
            
        success, message = UserService.add_to_favorites(current_user_id, product_id)
        
        if not success:
            api.abort(400, message)
        return {"message": message}, 200

    @jwt_required()
    @api.expect(product_id_payload)
    def delete(self):
        """Remove a product from user's favorites"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            api.abort(400, "Product ID is required")
            
        success, message = UserService.remove_from_favorites(current_user_id, product_id)
        
        if not success:
            api.abort(400, message)
        return {"message": message}, 200