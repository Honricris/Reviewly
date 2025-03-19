import os
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db
from google.oauth2 import id_token
from google.auth.transport import requests

class AuthService:
    @staticmethod
    def register_user(email, password):
        normalized_email = email.lower()
        if User.query.filter_by(email=normalized_email).first():
            return None, "User already exists", 409 

        password_hash = generate_password_hash(password)

        new_user = User(email=normalized_email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return new_user, None, 201  
    
    
    @staticmethod
    def login_user(email, password):
        normalized_email = email.lower()
        user = User.query.filter_by(email=normalized_email).first()

        if not user:
            return None, "User not found", 404  

        if not check_password_hash(user.password_hash, password):
            return None, "Invalid password", 401  

        return user, None, 200
    
    @staticmethod
    def google_auth(token):
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            email = idinfo['email']
            normalized_email = email.lower() 

            user = User.query.filter_by(email=normalized_email).first()


            if not user:
                user = User(email=normalized_email, password_hash=None)  
                db.session.add(user)
                db.session.commit()

            return user, None, 200

        except ValueError as e:
            return None, "Invalid Google token", 401