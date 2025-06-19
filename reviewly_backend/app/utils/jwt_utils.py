import jwt
from datetime import datetime, timedelta
from flask import current_app
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify
from functools import wraps

def generate_access_token(user):
    expiration = datetime.utcnow() + timedelta(hours=48)

    payload = {
        "sub": str(user.id), 
        "email": user.email if user.email else None,  
        "github_id": user.github_id if user.github_id else None, 
        "role": user.role,  
        "exp": expiration
    }

    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request() 
            claims = get_jwt()
            if claims.get('role') != 'admin':  
                return {"message": "Access forbidden: Admins only"}, 403  
            return fn(*args, **kwargs)
        return decorator
    return wrapper
