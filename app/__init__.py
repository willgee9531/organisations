# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.psuagwrbyzplvbagkntq:lagooz9531-@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'


    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.organisation import organisation_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(organisation_bp)

    return app
