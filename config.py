import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://mikol:mikol_password@localhost:5432/mikol_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mikol.db')


class ProductionConfig(Config):
    DEBUG = False

    # Handle postgres:// vs postgresql:// (Render/Railway compatibility)
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

    # Use SQLite as fallback if no DATABASE_URL
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///mikol_prod.db'

    # Base URL for share links
    BASE_URL = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('BASE_URL') or 'https://mikol.onrender.com'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
