from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db

class AuthService:
    @staticmethod
    def register_user(email, password):
        if User.query.filter_by(email=email).first():
            return None, "User already exists", 409 

        password_hash = generate_password_hash(password)

        new_user = User(email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return new_user, None, 201  
    
    
    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()

        if not user:
            return None, "User not found", 404  

        if not check_password_hash(user.password_hash, password):
            return None, "Invalid password", 401  

        return user, None, 200