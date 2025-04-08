from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api
from app.config import Config
from sqlalchemy import text
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask import jsonify
from flask_jwt_extended.exceptions import NoAuthorizationError


db = SQLAlchemy()

def check_required_env_vars():
    load_dotenv()  
    required_env_vars = ['DATABASE_URL', 'EDEN_API_TOKEN', 'EDEN_API_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

check_required_env_vars()

def create_app():
    app = Flask(__name__)
     # Configuración de CORS
    CORS(
        app,
        origins="http://localhost:5173",  
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  
        allow_headers=["Content-Type", "Authorization"],  
        supports_credentials=True  
    )

    API_PREFIX = '/api/v0'

    app.config.from_object(Config)

    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY') 
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 
    jwt = JWTManager(app)


    
    db.init_app(app)

    from app.models.user import User
    from app.models.product import Product
    from app.models.productdetail import ProductDetail
    from app.models.productfeature import ProductFeature
    from app.models.review import Review
    from app.models.amazonuser import AmazonUser
    from app.models.user_query import UserQuery

    api = Api(
        app,
        version="1.0",
        title="Reviewly API",
        description="Documentación de la API para gestionar productos, reseñas y chat.",
        doc="/"  
    )

    with app.app_context():
        try:
            db.create_all()
            db.session.execute(text('SELECT 1'))
            print("Conexión exitosa a la base de datos")
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")


    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"message": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        print(f"Invalid token callback: {callback}")
        return jsonify({"message": "Invalid token"}), 422
    
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        return jsonify({"message": "Missing Authorization Header"}), 401


    from app.routes import product_routes, review_routes, chat_routes, health_routes, auth_routes, user_queries
    api.add_namespace(product_routes.api, path=f"{API_PREFIX}/products")
    api.add_namespace(review_routes.api, path=f"{API_PREFIX}/reviews")
    api.add_namespace(chat_routes.api, path=f"{API_PREFIX}/chat")
    api.add_namespace(health_routes.api, path="/health")
    api.add_namespace(auth_routes.api, path=f"{API_PREFIX}/auth") 
    api.add_namespace(user_queries.api, path=f"{API_PREFIX}/user/queries") 


    return app
