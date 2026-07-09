import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "certpro-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "database", "certificates.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    CERTIFICATE_FOLDER = os.path.join(BASE_DIR, "static", "certificates_output")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SERVER_NAME = os.environ.get("SERVER_NAME")
