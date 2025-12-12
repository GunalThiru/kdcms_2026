# models/complaint_assignment.py
from datetime import datetime
from ..extensions import db
from .complaints import Complaint
from .users import User

class ComplaintAssignment(db.Model):
    __tablename__ = "complaint_assignment"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)

    # Relationships
    complaint = db.relationship(
        "Complaint",
        back_populates="assignments",
        overlaps="assignments"
    )
    assigned_by_user = db.relationship(
        "User",
        foreign_keys=[assigned_by],
        back_populates="assignments_given",
        overlaps="assignments_given"
    )
    assigned_to_user = db.relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assignments_received",
        overlaps="assignments_received"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "assigned_by": self.assigned_by,
            "assigned_to": self.assigned_to,
            "assigned_at": self.assigned_at.isoformat(),
            "remarks": self.remarks
        }
