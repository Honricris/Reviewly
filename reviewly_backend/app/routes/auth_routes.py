from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.LoginLog import LoginLog
from ..utils.jwt_utils import generate_access_token
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from sqlalchemy.sql import func

api = Namespace('auth', description='Auth related operations')

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
    @api.expect(register_model)  
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user_ip = request.remote_addr

        user, error, status_code = AuthService.register_user(email, password)
        if error:
            return {"message": error}, status_code

        login_log = LoginLog(
            user_id=user.id,
            ip_address=user_ip,
            login_at=func.now()
        )
        db.session.add(login_log)
        db.session.commit()

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
        user_ip = request.remote_addr  

        user, error, status_code = AuthService.login_user(email, password)
        if error:
            return {"message": error}, status_code

        login_log = LoginLog(
            user_id=user.id,
            ip_address=user_ip,
            login_at=func.now()
        )
        db.session.add(login_log)
        db.session.commit()

        access_token = generate_access_token(user)

        return {
            "message": "Inicio de sesión exitoso",
            "user_id": user.id,
            "email": user.email,
            "access_token": access_token
        }, 200
    
@api.route('/google')
class GoogleAuth(Resource):
    @api.expect(api.model('GoogleAuth', {
        'token': fields.String(required=True, description='Token de Google')
    }))
    def post(self):
        data = request.get_json()
        token = data.get('token')
        user_ip = request.remote_addr  

        user, error, status_code = AuthService.google_auth(token)
        if error:
            return {"message": error}, status_code

        login_log = LoginLog(
            user_id=user.id,
            ip_address=user_ip,
            login_at=func.now()
        )
        db.session.add(login_log)
        db.session.commit()

        access_token = generate_access_token(user)

        return {
            "message": "Autenticación con Google exitosa",
            "user_id": user.id,
            "email": user.email,
            "access_token": access_token
        }, 200
    
github_auth_model = api.model('GitHubAuth', {
    'code': fields.String(required=True, description='Código de GitHub')
})

@api.route('/github')
class GitHubAuth(Resource):
    @api.expect(github_auth_model)
    def post(self):
        data = request.get_json()
        code = data.get('code')
        user_ip = request.remote_addr  

        user, error, status_code = AuthService.github_auth(code)
        if error:
            return {"message": error}, status_code

        login_log = LoginLog(
            user_id=user.id,
            ip_address=user_ip,
            login_at=func.now()
        )
        db.session.add(login_log)
        db.session.commit()

        access_token = generate_access_token(user)

        return {
            "message": "Autenticación con GitHub exitosa",
            "user_id": user.id,
            "email": user.email,
            "access_token": access_token
        }, 200
    
logout_model = api.model('Logout', {
    'message': fields.String(description='Mensaje de confirmación')
})

@api.route('/logout')
class Logout(Resource):
    @jwt_required()
    @api.response(200, 'Success', logout_model)
    def post(self):
        current_user_id = get_jwt_identity()
        
        from app.services.chat_service_v2 import ChatService
        ChatService.remove_instance(current_user_id)
        
        return {
            "message": "Sesión cerrada exitosamente. Sesión de chat eliminada."
        }, 200