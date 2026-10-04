import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/skillscreen_db'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__dirname__)) if '__dirname__' in locals() else os.path.dirname(os.path.abspath(__file__)), 'uploads')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
