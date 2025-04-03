import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_access_token(user):
    expiration = datetime.utcnow() + timedelta(hours=2)

    payload = {
        "sub": str(user.id), 
        "email": user.email if user.email else None,  
        "github_id": user.github_id if user.github_id else None, 
        "role": user.role,  
        "exp": expiration
    }

    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token
