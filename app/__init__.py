from flask import Flask
from .config import Config
from .extensions import db, migrate
from . import models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.interview import interview_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(interview_bp)

    return app
