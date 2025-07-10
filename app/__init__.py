from flask import Flask
from datetime import timedelta
from flask_migrate import Migrate
from .models import db

migrate = Migrate()  # Initialize without app

def create_app():
    app = Flask(__name__)

    # Secret key for session security
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Session lifetime config (user stays logged in for 7 days)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # Bind app and db here

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()  # Optional if you're using Flask-Migrate, but fine for first-time setup

    return app
