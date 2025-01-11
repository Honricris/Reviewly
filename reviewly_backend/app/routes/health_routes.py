from flask import Blueprint, jsonify
from sqlalchemy import text
from app import db
import os

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    health_status = {
        "database": False,
        "env_vars": True
    }

    # Verificar variables de entorno
    required_env_vars = ['DATABASE_URL', 'EDEN_API_TOKEN', 'EDEN_API_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        health_status["env_vars"] = False

    # Verificar conexión a la base de datos
    try:
        db.session.execute(text('SELECT 1'))
        health_status["database"] = True
    except Exception as e:
        health_status["database"] = False
        health_status["error"] = str(e)

    status_code = 200 if health_status["database"] and health_status["env_vars"] else 500
    return jsonify(health_status), status_code
