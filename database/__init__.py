from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        from database.models import User, Student, Course, Enrollment
        from database.models import Marks, Prediction, Certificate, VerificationLog
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
