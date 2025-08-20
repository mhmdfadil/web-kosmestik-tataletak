import os
from flask import Flask
from flask_cors import CORS
from apps.database.database import mysql
from config import Config

def create_app():
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config.from_object(Config)

    # Menampilkan konfigurasi yang sedang digunakan (untuk debugging)
    print("Flask Configuration:")
    print(f"  - Debug: {app.config['DEBUG']}")
    print(f"  - Pengembangan: {app.config['ENV']}")
    print(f"  - Secret Key: {app.config['SECRET_KEY']}")
    print(f"  - MySQL Host: {app.config['MYSQL_HOST']}")
    print(f"  - MySQL User: {app.config['MYSQL_USER']}")
    print(f"  - MySQL DB: {app.config['MYSQL_DB']}")
    
    # Konfigurasi UPLOAD_FOLDER
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Konfigurasi MySQL
    app.config["MYSQL_HOST"] = Config.MYSQL_HOST
    app.config["MYSQL_USER"] = Config.MYSQL_USER
    app.config["MYSQL_PASSWORD"] = Config.MYSQL_PASSWORD
    app.config["MYSQL_DB"] = Config.MYSQL_DB

    mysql.init_app(app)
    CORS(app)

    # Register blueprint dari routes
    from apps.routes.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app