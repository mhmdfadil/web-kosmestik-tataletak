import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "apps", "static", "uploads")
    ENV = os.getenv("FLASK_ENVIRONMENT")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    MYSQL_HOST = os.getenv("FLASK_HOST")
    MYSQL_USER = os.getenv("FLASK_USERNAME")
    MYSQL_PASSWORD = os.getenv("FLASK_PASSWORD")
    MYSQL_DB = os.getenv("FLASK_DATABASE")
