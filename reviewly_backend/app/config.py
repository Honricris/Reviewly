import os

class Config:
    # Cargar la URL de la base de datos desde el entorno
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # Configuración para desactivar las notificaciones de cambios de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para la aplicación Flask (importante para sesiones o CSRF)
    SECRET_KEY = os.getenv("SECRET_KEY",  os.urandom(24))
