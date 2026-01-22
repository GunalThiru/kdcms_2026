import os

# -------------------------
# Base configuration
# -------------------------
class Config:
    """
    Base configuration class.
    Contains settings common to all environments.
    """

    # Disable SQLAlchemy event system (better performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for sessions and security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')

    # File upload directory (for complaint attachments)
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

    # Maximum upload size: 50MB
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # JWT secret key
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
# -------------------------
# Development configuration
# -------------------------
class DevelopmentConfig(Config):
    """
    Configuration for local development.
    Inherits from Config base class.
    """

    # Database connection string (YOUR NEW DB NAME)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/kdmbcms'

    # Enable debug mode
    DEBUG = True


# -------------------------
# Production configuration
# -------------------------
class ProductionConfig(Config):
    """
    Production configuration for deployment.
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/kdmbcms'
    )

    DEBUG = False


# -------------------------
# Mode selection
# -------------------------
config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
