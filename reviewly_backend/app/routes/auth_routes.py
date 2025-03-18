from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from app.services.auth_service import AuthService
from app.models.user import User
from ..utils.jwt_utils import generate_access_token
from flask import current_app

api = Namespace('auth', description='Operaciones de autenticación')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Correo electrónico del usuario'),
    'password': fields.String(required=True, description='Contraseña del usuario')
})

register_model = api.model('Register', {
    'email': fields.String(required=True, description='Correo electrónico del usuario'),
    'password': fields.String(required=True, description='Contraseña del usuario')
})

@api.route('/register')
class Register(Resource):
    @api.expect(register_model)  #
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user, error, status_code = AuthService.register_user(email, password)
        if error:
            return {"message": error}, status_code

        access_token = generate_access_token(user)

        return {
            "message": "Usuario registrado exitosamente",
            "user_id": user.id,
            "email": user.email,
            "access_token": access_token
        }, 201
    
    
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user, error, status_code = AuthService.login_user(email, password)
        if error:
            return {"message": error}, status_code

        access_token = generate_access_token(user)

        return {
            "message": "Inicio de sesión exitoso",
            "user_id": user.id,
            "email": user.email,
            "access_token": access_token
        }, 200