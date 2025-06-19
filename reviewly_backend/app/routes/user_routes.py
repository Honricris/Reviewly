from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.services.user_service import UserService
from app.models.LoginLog import LoginLog
from app.utils.jwt_utils import admin_required

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

user_model = api.model('User', {
    'id': fields.Integer(readonly=True),
    'email': fields.String(required=True),
    'role': fields.String(required=True),
    'github_id': fields.Integer(),
    'created_at': fields.DateTime(readonly=True)
})

user_input_model = api.model('UserInput', {
    'email': fields.String(required=True, description='User email'),
    'role': fields.String(required=True, description='User role (user or admin)'),
    'github_id': fields.Integer(description='GitHub ID if applicable')
})

@api.route('/favorites')
class UserFavorites(Resource):
    @jwt_required()
    def get(self):
        """Get list of user's favorite product IDs"""
        current_user_id = get_jwt_identity()
        favorite_ids, error = UserService.get_user_favorite_ids(current_user_id)
        
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

@api.route('')
class UserList(Resource):
    @jwt_required()
    @admin_required()
    @api.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        users = UserService.get_users()
        return users

    @jwt_required()
    @api.expect(user_input_model)
    @api.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        data = request.get_json()
        user, error = UserService.create_user(
            email=data.get('email'),
            role=data.get('role'),
            github_id=data.get('github_id')
        )
        
        if error:
            api.abort(400, error)
        return user, 201

@api.route('/<int:user_id>')
class UserResource(Resource):
    @jwt_required()
    @api.marshal_with(user_model)
    def get(self, user_id):
        """Get a specific user"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            api.abort(404, "User not found")
        return user

    @jwt_required()
    @api.expect(user_input_model)
    @api.marshal_with(user_model)
    def put(self, user_id):
        """Update a user"""
        data = request.get_json()
        user, error = UserService.update_user(
            user_id=user_id,
            email=data.get('email'),
            role=data.get('role'),
            github_id=data.get('github_id')
        )
        
        if error:
            api.abort(400, error)
        if not user:
            api.abort(404, "User not found")
        return user

    @jwt_required()
    @admin_required()
    def delete(self, user_id):
        """Delete a user"""
        success, message = UserService.delete_user(user_id)
        if not success:
            api.abort(404, message)
        return {"message": message}, 200
    

@api.route('/<int:user_id>/favorites')
class UserSpecificFavorites(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = UserService.get_user_by_id(current_user_id)
        if current_user.role != 'admin':
            api.abort

        """Get list of favorite product IDs for a specific user"""
        favorite_ids, error = UserService.get_user_favorite_ids(user_id)
        
        if error:
            api.abort(404, error)
        return favorite_ids
    
login_log_model = api.model('LoginLog', {
    'id': fields.Integer(description='Log ID'),
    'user_id': fields.Integer(description='User ID'),
    'ip_address': fields.String(description='IP Address'),
    'login_at': fields.DateTime(description='Login Timestamp')
})

@api.route('/<int:user_id>/login-logs')
class UserLoginLogs(Resource):
    @jwt_required()
    @api.marshal_list_with(login_log_model)
    def get(self, user_id):
        """Get all login logs for a specific user"""
        try:
            logs = LoginLog.query.filter_by(user_id=user_id)\
                                .order_by(LoginLog.login_at.desc())\
                                .all()
            if not logs:
                return [], 200 
            return logs, 200
        except Exception as e:
            return {"error": str(e)}, 500
        
login_log_model = api.model('LoginLog', {
    'id': fields.Integer(description='Log ID'),
    'user_id': fields.Integer(description='User ID'),
    'ip_address': fields.String(description='IP Address'),
    'login_at': fields.DateTime(description='Login Timestamp')
})

@api.route('/<int:user_id>/login-logs')
class UserLoginLogs(Resource):
    @jwt_required()
    @api.marshal_list_with(login_log_model)
    def get(self, user_id):
        """Get all login logs for a specific user"""
        try:
            logs = LoginLog.query.filter_by(user_id=user_id)\
                                .order_by(LoginLog.login_at.desc())\
                                .all()
            if not logs:
                return [], 200  
            return logs, 200
        except Exception as e:
            return {"error": str(e)}, 500