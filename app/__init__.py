from flask import Flask
import os
import secrets
from dotenv import load_dotenv
from .extensions import db, login_manager
from .models import User

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database configuration - Use PostgreSQL in production, SQLite for local dev
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render provides PostgreSQL URL, may need to convert from postgres:// to postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edudap.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 10485760))  # 10MB
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'bills'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'quotes'), exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from .employee import employee_bp
    app.register_blueprint(employee_bp)
    
    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from .quote import quote_bp
    app.register_blueprint(quote_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
