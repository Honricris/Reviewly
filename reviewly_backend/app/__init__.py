from dotenv import load_dotenv
import os

def check_required_env_vars():
    load_dotenv() 
    required_env_vars = ['DATABASE_URL', 'EDEN_API_TOKEN', 'EDEN_API_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

check_required_env_vars()


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from sqlalchemy import text
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    API_PREFIX = '/api/v0'

    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Verificar la conexión a la base de datos
    with app.app_context():
        try:
            # Comprobamos la conexión
            db.session.execute(text('SELECT 1'))
            print("Conexión exitosa a la base de datos")
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
    
    # Registrar blueprints
    from app.routes import product_routes, review_routes, chat_routes, health_routes
    app.register_blueprint(product_routes.bp, url_prefix=API_PREFIX)
    app.register_blueprint(review_routes.bp, url_prefix=API_PREFIX)
    app.register_blueprint(chat_routes.bp, url_prefix=API_PREFIX)
    app.register_blueprint(health_routes.bp)

    return app
