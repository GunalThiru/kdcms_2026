from flask import Flask, request, make_response
from flask_cors import CORS
from backend.extensions import db, jwt
from backend.routes import register_routes
from backend.config import config


def create_app():
    app = Flask(__name__)

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/kdmbcms"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Connection pooling and timeout settings for reliability
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,  # Test connection before using
        "connect_args": {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
        }
    }

    # 🔐 JWT CONFIG (THIS FIXES YOUR ERROR)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change later
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True
    )

    # Handle OPTIONS preflight
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response

    # -------------------------------------------------
    # INIT EXTENSIONS
    # -------------------------------------------------
    db.init_app(app)
    jwt.init_app(app)   # 🔥 THIS WAS MISSING

    # -------------------------------------------------
    # ROUTES
    # -------------------------------------------------
    register_routes(app)

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize database: {e}")
            print("Start MySQL and restart the app to enable database features.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
