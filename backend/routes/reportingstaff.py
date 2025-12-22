from flask import Blueprint, jsonify
from ..extensions import db
from ..models.users import User
from ..models.reporting_staff import ReportingStaff

reporting_staff_bp = Blueprint(
    "reporting_staff",
    __name__,
    url_prefix="/reporting-staff"
)

@reporting_staff_bp.route("", methods=["GET"])
def get_reporting_staff():
    staff = (
        db.session.query(User.id, User.name)
        .join(ReportingStaff, ReportingStaff.user_id == User.id)
        .filter(ReportingStaff.active == True)
        .all()
    )

    return jsonify([
        {
            "user_id": s.id,
            "name": s.name
        } for s in staff
    ])
