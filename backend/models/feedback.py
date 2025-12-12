from datetime import datetime
from ..extensions import db

class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id", ondelete="CASCADE"), unique=True, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    staff = db.relationship("User", foreign_keys=[staff_id])
    customer = db.relationship("User", foreign_keys=[customer_id])
    complaint = db.relationship("Complaint", foreign_keys=[complaint_id])

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "staff_id": self.staff_id,
            "customer_id": self.customer_id,
            "rating": self.rating,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
