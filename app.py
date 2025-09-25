from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pathlib import Path
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance folder exists for SQLite
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # Import models so tables are known
    from models.user import User  # noqa
    from models.expense import Expense  # noqa

    # Register blueprints
    from routes.auth import auth_bp
    from routes.expense import expense_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(dashboard_bp)

    # Create tables on first run
    with app.app_context():
        db.create_all()

    return app
