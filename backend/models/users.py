# backend/models/users.py
from datetime import datetime, timezone
from ..extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)   # Make sure this column exists in DB
    age = db.Column(db.Integer)  # Make sure this column exists in DB
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

     # Relationships for Complaints
    complaints_reported = db.relationship(
        "Complaint",
        foreign_keys="Complaint.reported_by",
        back_populates="reporter",
        overlaps="reporter"
    )
    complaints_resolved = db.relationship(
        "Complaint",
        foreign_keys="Complaint.resolved_by",
        back_populates="resolver",
        overlaps="resolver"
    )

    # Relationships for Assignments (ComplaintAssignment)
    assignments_given = db.relationship(
        "ComplaintAssignment",
        foreign_keys="ComplaintAssignment.assigned_by",
        back_populates="assigned_by_user",  # matches ComplaintAssignment
        overlaps="assigned_by_user"
    )
    assignments_received = db.relationship(
        "ComplaintAssignment",
        foreign_keys="ComplaintAssignment.assigned_to",
        back_populates="assigned_to_user",  # matches ComplaintAssignment
        overlaps="assigned_to_user"
    )

    # Relationships for Feedback
    feedback_given = db.relationship(
        "Feedback",
        foreign_keys="Feedback.customer_id",
        back_populates="customer",
        overlaps="customer"
    )
    feedback_received = db.relationship(
        "Feedback",
        foreign_keys="Feedback.staff_id",
        back_populates="staff",
        overlaps="staff"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": getattr(self, "phone", None),
            "password_hash": getattr(self, "password_hash", None),
            "role": getattr(self, "role", None),
            "gender": self.gender,
            "dob": str(self.dob) if self.dob else None,
            "age": self.age,
            "is_online": getattr(self, "is_online", None),
            "last_seen": getattr(self, "last_seen", None).isoformat() if getattr(self, "last_seen", None) else None,
            "is_active": getattr(self, "is_active", None),
            "created_at": getattr(self, "created_at", datetime.utcnow()).isoformat(),
        }