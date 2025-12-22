from flask import Flask, request, make_response
from flask_cors import CORS
from backend.extensions import db, jwt
from backend.routes import register_routes


def create_app():
    app = Flask(__name__)

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/kdmbcms"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
