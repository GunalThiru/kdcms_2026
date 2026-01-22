from datetime import datetime
from backend.extensions import db

class ComplaintEmailConfig(db.Model):
    __tablename__ = 'complaint_email_config'

    id = db.Column(db.Integer, primary_key=True)

    problem_type = db.Column(
        db.String(50),
        nullable=False,
        unique=True  # one rule per problem type
    )

    to_email = db.Column(
        db.String(255),
        nullable=False
    )

    cc_email = db.Column(
        db.String(255),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return (
            f"<ComplaintEmailConfig "
            f"id={self.id}, "
            f"problem_type={self.problem_type}, "
            f"active={self.is_active}>"
        )