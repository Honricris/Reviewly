import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_access_token(user_id):
    expiration = datetime.utcnow() + timedelta(hours=1)
    
    payload = {
        "user_id": user_id,
        "exp": expiration
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token