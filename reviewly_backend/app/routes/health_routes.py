from flask_restx import Namespace, Resource
from sqlalchemy import text
from app import db
import os

api = Namespace('health', description='Health check operations')

@api.route('/')
class HealthCheck(Resource):
    def get(self):
        health_status = {
            "database": False,
            "env_vars": True
        }

        required_env_vars = ['DATABASE_URL']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            health_status["env_vars"] = False

        try:
            db.session.execute(text('SELECT 1'))
            health_status["database"] = True
        except Exception as e:
            health_status["database"] = False
            health_status["error"] = str(e)

        status_code = 200 if health_status["database"] and health_status["env_vars"] else 500
        return health_status, status_code
