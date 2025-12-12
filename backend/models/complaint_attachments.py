from datetime import datetime
from ..extensions import db
from .complaints import Complaint
import os

class ComplaintAttachment(db.Model):
    __tablename__ = "complaint_attachments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False
    )
    
    filename = db.Column(db.String(255), nullable=False)   # NEW (not in DB but required)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)    # IN YOUR TABLE
    file_size = db.Column(db.Integer, nullable=False)    # IN YOUR TABLE

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship(
        "Complaint",
        back_populates="attachments",
        overlaps="attachments"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at.isoformat()
        }
