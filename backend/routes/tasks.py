from flask import Blueprint, jsonify
from backend.extensions import db
from backend.models import Complaint, ComplaintAttachment
from backend.models.complaint_status_master import ComplaintStatus
from flask_jwt_extended import jwt_required, get_jwt_identity


task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@task_bp.route('', methods=['GET'])
def get_tasks():
    tasks = (
        db.session.query(Complaint)
        .join(ComplaintStatus)
        .filter(ComplaintStatus.code.in_(["PENDING", "IN_PROGRESS"]))
        .order_by(Complaint.created_at.desc())
        .all()
    )

    result = []
    for c in tasks:
        task_dict = {
    "id": c.id,
    "problem_description": c.problem_description,
    "problem_type": c.problem_type,
    "sub_problem_type": c.sub_problem_type,
    "status": c.status.code,
    "created_at": c.created_at.isoformat(),
    "reference_type": c.reference_type,
    "reference_no": c.reference_id,
    "reported_by": c.reporter.name if c.reporter else None,   # show name
    "resolved_by": c.resolver.name if c.resolver else None,   # show name
    "date_of_issue": c.date_of_issue.isoformat(),
    "reporting_time": c.reporting_time.strftime("%H:%M:%S"),
    "reporting_mode": c.reporting_mode,
    "remarks": c.remarks,
    "solution_provided": c.solution_provided
}


        # add attachments
        attachments = (
            db.session.query(ComplaintAttachment)
            .filter(ComplaintAttachment.complaint_id == c.id)
            .all()
        )

        task_dict["attachments"] = [
    {
        "id": a.id,
        "file_name": a.filename,
        "file_url": f"http://localhost:5000/complaints/uploads/complaints/{a.filename}"
    }
    for a in attachments
        ]

        result.append(task_dict)

    return jsonify(result), 200

@task_bp.route('/count', methods=['GET'])
def get_open_tasks_count():
    count = (
        db.session.query(Complaint)
        .join(ComplaintStatus)
        .filter(ComplaintStatus.code.in_(["PENDING", "IN_PROGRESS"]))
        .count()
    )

    return jsonify({"open_tasks": count}), 200




# @task_bp.route('/<int:task_id>/start', methods=['POST'])
# @jwt_required()
# def start_task(task_id):
#     complaint = Complaint.query.get_or_404(task_id)

#     in_progress_status = ComplaintStatus.query.filter_by(code="IN_PROGRESS").first()

#     if complaint.status.code == "PENDING":
#         complaint.status_id = in_progress_status.id
#         db.session.commit()

#     return jsonify({"message": "Task marked in progress"}), 200

@task_bp.route('/<int:task_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_task(task_id):
    current_user_id = get_jwt_identity()  # ✅ LOGGED-IN STAFF

    complaint = Complaint.query.get_or_404(task_id)
    resolved_status = ComplaintStatus.query.filter_by(code="RESOLVED").first()

    complaint.status_id = resolved_status.id
    complaint.resolved_by = current_user_id
    complaint.solution_provided = db.session.get(Complaint, task_id).solution_provided

    db.session.commit()

    return jsonify({
        "message": "Complaint resolved",
        "resolved_by": current_user_id
    }), 200


