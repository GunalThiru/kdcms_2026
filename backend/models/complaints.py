from datetime import datetime
from ..extensions import db
from sqlalchemy.sql import text
from sqlalchemy import Enum as PgEnum

# -------------------------
# ENUMS
# -------------------------

PROBLEM_TYPE_CODE = {
    "bus_service": "BUS",
    "smartcity_card": "SCC",
    "ktcl_smart_card": "KSC",
    "smart_pass": "KSP",
    "tickets": "TKT",
    "staff": "STF",
    "others": "OTH"
}

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

reference_type_enum = PgEnum(
    'app_no',
    'card_no',
    'utr',
    
    name="reference_type_enum"
)

reporting_mode_enum = PgEnum(
    'mail',
    'call',
    'message',
    'app',
    name="reporting_mode_enum"
)

# -------------------------
# COMPLAINT MODEL
# -------------------------
class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    complaint_no = db.Column(db.String(20), unique=True, nullable=False)

    # Complaint details
    date_of_issue = db.Column(db.Date, nullable=False)
    reporting_time = db.Column(db.Time, nullable=False)
    reporting_mode = db.Column(reporting_mode_enum, nullable=False)

    problem_type = db.Column(problem_type_enum, nullable=False)
    sub_problem_type = db.Column(sub_problem_type_enum, nullable=False)

    reference_type = db.Column(reference_type_enum, nullable=False)
    reference_id = db.Column(db.String(100), nullable=False)

    problem_description = db.Column(db.Text, nullable=False)
    solution_provided = db.Column(db.Text)
    solution_date_time = db.Column(db.DateTime)

    # -------------------------
    # USER REFERENCES (NULLABLE FOR GUEST)
    # -------------------------
    resolved_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    reported_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True   # Guest reports will have NULL
    )

    # -------------------------
    # GUEST FIELDS
    # -------------------------
    is_guest = db.Column(db.Boolean, nullable=False, server_default=text("FALSE"))
    reporter_name = db.Column(db.String(100), nullable=True)
    guest_mobile = db.Column(db.String(15), nullable=True)
    guest_email = db.Column(db.String(100), nullable=True)

    remarks = db.Column(db.Text)

    # Complaint status
    status_id = db.Column(
        db.Integer,
        db.ForeignKey("complaint_status_master.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("NOW()")
    )

    # -------------------------
    # RELATIONSHIPS
    # -------------------------
    resolver = db.relationship(
        "User",
        foreign_keys=[resolved_by],
        back_populates="complaints_resolved",
        overlaps="complaints_resolved"
    )

    reporter = db.relationship(
        "User",
        foreign_keys=[reported_by],
        back_populates="complaints_reported",
        overlaps="complaints_reported"
    )

    status = db.relationship(
        "ComplaintStatus",
        back_populates="complaints"
    )

    attachments = db.relationship(
        "ComplaintAttachment",
        cascade="all, delete",
        back_populates="complaint",
        overlaps="complaint"
    )

    assignments = db.relationship(
        "ComplaintAssignment",
        cascade="all, delete",
        back_populates="complaint",
        overlaps="complaint"
    )

    feedback = db.relationship(
        "Feedback",
        uselist=False,
        cascade="all, delete",
        back_populates="complaint",
        overlaps="complaint"
    )
    email_logs = db.relationship(
        'ComplaintEmailLog',
        back_populates='complaint',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # -------------------------
    # TO DICT
    # -------------------------
    def to_dict(self, include_resolved_by=True):
        return {
            "id": self.id,
            "complaint_no": self.complaint_no,
            
            "date_of_issue": str(self.date_of_issue),
            "reporting_time": str(self.reporting_time),
            "reporting_mode": self.reporting_mode,

            "problem_type": self.problem_type,
            "sub_problem_type": self.sub_problem_type,

            "reference_type": self.reference_type,
            "reference_id": self.reference_id,

            "problem_description": self.problem_description,
            "solution_provided": self.solution_provided,
            "solution_date_time": self.solution_date_time.isoformat() if self.solution_date_time else None,
             # guest details
            "is_guest": self.is_guest,

            "reported_by": self.reported_by,


            "reporter_name": self.reporter.name if self.reporter else self.reporter_name,
           
            "guest_mobile": self.reference_id if self.is_guest and self.reference_type == 'mobile' else None,
            "guest_email": self.reference_id if self.is_guest and self.reference_type == 'email' else None,

            **({"resolved_by": self.resolved_by} if include_resolved_by else {}),

            "remarks": self.remarks,
            "status": self.status.code if self.status else None,
            "created_at": self.created_at.isoformat(),

            "attachments": [
                {
                    "file_name": a.filename,
                    "file_type": a.file_type,
                    "file_size": a.file_size,
                    "file_url": f"http://localhost:5000/complaints/uploads/complaints/{a.filename}"
                }
                for a in self.attachments
            ],

            "assignments": [a.to_dict() for a in self.assignments],
            "feedback": self.feedback.to_dict() if self.feedback else None
        }
