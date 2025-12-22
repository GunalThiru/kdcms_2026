def register_routes(app):
    from .auth import auth_bp
    # from .user import user_bp
    from .complaint_form import complaint_bp
    from .complaint_attachment import attachment_bp

    from .reportingstaff import reporting_staff_bp
    # from .feedback import feedback_bp
    from .profile import profile_bp
    from .tasks import task_bp



    app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)
    app.register_blueprint(complaint_bp)
    # app.register_blueprint(feedback_bp)
    app.register_blueprint(attachment_bp)
    app.register_blueprint(reporting_staff_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(task_bp)

    @app.route("/")
    def home():
         return {"message": "Backend API is running"}, 200

