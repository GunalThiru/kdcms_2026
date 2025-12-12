from datetime import datetime
from ..extensions import db


from sqlalchemy import Enum as PgEnum

# Enums
problem_type_enum = PgEnum(
    'smartcity_card',
    'ktcl_smart_card',
    'smart_pass',
    'tickets',
    'bus_service',
    'staff',
    'others',
    name="problem_type_enum"
)
sub_problem_type_enum = PgEnum(
    'website_recharge',
    'mobile_app_recharge',
    'etim_val_recharge',
    'application',
    'smartcity_card_recharge',
    'lost_card',
    'damaged_card',
    'refund',
    'others',

    'smart_pass_application',
    'smart_pass_renewal_website',
    'smart_pass_renewal_mobile_app',
    'smart_pass_wallet_recharge',
    'change_personal_details',
    'change_pass_details',
    'lost_pass',
    'damaged_pass',

    'mobile_ticket_issue',
    'upi_ticket_issue',

    'service_complaint',
    'driver_behaviour',
    'conductor_behaviour',

    'staff_behaviour',
    'service_delay',

    'general_complaint',
    name="sub_problem_type_enum"
)

reference_type_enum = PgEnum('app_no', 'card_no', 'email', 'utr','mobile', name="reference_type_enum")
reporting_mode_enum = PgEnum('mail', 'call', 'message', 'app', name="reporting_mode_enum")

class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    date_of_issue = db.Column(db.Date, nullable=False)
    reporting_time = db.Column(db.Time, nullable=False)
    reporting_mode = db.Column(reporting_mode_enum, nullable=False)
    problem_type = db.Column(problem_type_enum, nullable=False)
    sub_problem_type = db.Column(sub_problem_type_enum, nullable=False)
    reference_type = db.Column(reference_type_enum, nullable=False)
    reference_id = db.Column(db.String(100))
    problem_description = db.Column(db.Text, nullable=False)
    solution_provided = db.Column(db.Text)
    solution_date_time = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    reported_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resolver = db.relationship("User", foreign_keys=[resolved_by], back_populates="complaints_resolved", overlaps="complaints_resolved")
    reporter = db.relationship("User", foreign_keys=[reported_by], back_populates="complaints_reported", overlaps="complaints_reported")
    attachments = db.relationship("ComplaintAttachment", cascade="all, delete", back_populates="complaint", overlaps="complaint")
    assignments = db.relationship("ComplaintAssignment", cascade="all, delete", back_populates="complaint", overlaps="complaint")
    feedback = db.relationship("Feedback", uselist=False, cascade="all, delete", back_populates="complaint", overlaps="complaint")

    def to_dict(self):
        return {
            "id": self.id,
            "date_of_issue": str(self.date_of_issue),
            "reporting_time": str(self.reporting_time),
            "reporting_mode": self.reporting_mode,
            "problem_type": self.problem_type,
            "sub_problem_type": self.sub_problem_type,
            "reference_type": self.reference_type,
            "reference_no": self.reference_id,
            "problem_description": self.problem_description,
            "solution_provided": self.solution_provided,
            "solution_date_time": self.solution_date_time.isoformat() if self.solution_date_time else None,
            "reported_by": self.reported_by,
            "resolved_by": self.resolved_by,
            "remarks": self.remarks,
            "created_at": self.created_at.isoformat(),
            "attachments": [a.to_dict() for a in self.attachments],
            "assignments": [a.to_dict() for a in self.assignments],
            "feedback": self.feedback.to_dict() if self.feedback else None
        }
