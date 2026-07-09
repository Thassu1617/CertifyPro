from flask import Flask
from flask_login import LoginManager
from config import Config
from database import db
from database.models import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from database import models
        db.create_all()
        if not User.query.filter_by(role="admin").first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username="admin",
                email="admin@certifypro.com",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                full_name="System Administrator",
            )
            db.session.add(admin)
            db.session.commit()
        try:
            from database.models import Course
            if not Course.query.first():
                from seed_data import seed
                seed()
        except Exception:
            pass

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.student import student_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(student_bp, url_prefix="/student")

    return app
