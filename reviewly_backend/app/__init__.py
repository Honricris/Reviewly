from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api
from app.config import Config
from sqlalchemy import text
from dotenv import load_dotenv
import os

# Inicializar SQLAlchemy
db = SQLAlchemy()

def check_required_env_vars():
    load_dotenv()  
    required_env_vars = ['DATABASE_URL', 'EDEN_API_TOKEN', 'EDEN_API_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

# Verificar que las variables de entorno requeridas estén definidas
check_required_env_vars()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Prefijo de la API
    API_PREFIX = '/api/v0'

    # Configuración de la aplicación
    app.config.from_object(Config)
    db.init_app(app)

    # Crear instancia de Flask-RESTx
    api = Api(
        app,
        version="1.0",
        title="Reviewly API",
        description="Documentación de la API para gestionar productos, reseñas y chat.",
        doc="/"  
    )

    # Verificar la conexión a la base de datos
    with app.app_context():
        try:
            db.create_all()
            db.session.execute(text('SELECT 1'))
            print("Conexión exitosa a la base de datos")
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")

    # Registrar namespaces de Flask-RESTx
    from app.routes import product_routes, review_routes, chat_routes, health_routes
    api.add_namespace(product_routes.api, path=f"{API_PREFIX}/products")
    api.add_namespace(review_routes.api, path=f"{API_PREFIX}/reviews")
    api.add_namespace(chat_routes.api, path=f"{API_PREFIX}/chat")
    api.add_namespace(health_routes.api, path="/health")

    return app
