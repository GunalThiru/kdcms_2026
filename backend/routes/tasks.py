from flask import Blueprint, jsonify
from backend.extensions import db
from backend.models import Complaint, ComplaintAttachment
from backend.models.complaint_status_master import ComplaintStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.users import User
from backend.models.complaint_views import ComplaintView
from sqlalchemy import func
from datetime import datetime,timezone
from backend.models import db   
from flask import request
import math


import pytz



# helper
def ist_dt():
    
    return datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)


task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@task_bp.route('', methods=['GET'])
def get_tasks():
    # Get filter and pagination parameters
    status = request.args.get('status', '').upper()
    problem_type = request.args.get('problem_type', '')
    sub_problem_type = request.args.get('sub_problem_type', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)

    # ✅ SUBQUERY: last view per complaint
    last_view_subq = (
        db.session.query(
            ComplaintView.complaint_id,
            func.max(ComplaintView.viewed_at).label("last_viewed_at")
        )
        .group_by(ComplaintView.complaint_id)
        .subquery()
    )

    # ✅ MAIN QUERY
    query = (
        db.session.query(
            Complaint,
            ComplaintView,
            last_view_subq.c.last_viewed_at
        )
        .join(ComplaintStatus)
        .outerjoin(
            last_view_subq,
            last_view_subq.c.complaint_id == Complaint.id
        )
        .outerjoin(
            ComplaintView,
            (ComplaintView.complaint_id == Complaint.id) &
            (ComplaintView.viewed_at == last_view_subq.c.last_viewed_at)
        )
        .filter(ComplaintStatus.code.in_(["PENDING", "IN_PROGRESS"]))
    )

    # Apply filters
    if status and status in ["PENDING", "IN_PROGRESS"]:
        query = query.filter(ComplaintStatus.code == status)
    
    if problem_type:
        query = query.filter(Complaint.problem_type == problem_type)
    
    if sub_problem_type:
        query = query.filter(Complaint.sub_problem_type == sub_problem_type)
    
    if from_date:
        try:
            from_date_obj = datetime.fromisoformat(from_date).date()
            query = query.filter(Complaint.date_of_issue >= from_date_obj)
        except:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.fromisoformat(to_date).date()
            query = query.filter(Complaint.date_of_issue <= to_date_obj)
        except:
            pass
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Complaint.complaint_no.ilike(search_term),
                Complaint.problem_description.ilike(search_term),
                Complaint.reporter_name.ilike(search_term)
            )
        )

    # Get total count before pagination
    total_count = query.count()

    # Apply ordering and pagination
    tasks = (
        query
        .order_by(Complaint.created_at.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    result = []

    for c, last_view, last_viewed_at in tasks:
        task_dict = {
            "id": c.id,
            "complaint_no": c.complaint_no,
            "problem_description": c.problem_description,
            "problem_type": c.problem_type,
            "sub_problem_type": c.sub_problem_type,
            "status": c.status.code,
            "created_at": c.created_at.isoformat(),
            "reference_type": c.reference_type,
            "reference_no": c.reference_id,
            "reported_by": c.reporter.name if c.reporter else None,
            "resolved_by": c.resolver.name if c.resolver else None,
            "is_guest": c.is_guest,
            "reporter_name": c.reporter_name,
            "date_of_issue": c.date_of_issue.isoformat() if c.date_of_issue else None,
            "reporting_time": c.reporting_time.strftime("%H:%M:%S") if c.reporting_time else None,
            "reporting_mode": c.reporting_mode,
            "remarks": c.remarks,
            "solution_provided": c.solution_provided,

            # ✅ NEW FIELDS
            "last_viewed_by": last_view.viewer.name if last_view and last_view.viewer else None,
            "last_viewed_at": last_viewed_at.isoformat() if last_viewed_at else None
        }

        # attachments (unchanged)
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

    # Calculate total pages
    total_pages = math.ceil(total_count / pageSize) if pageSize > 0 else 0

    return jsonify({
        "data": result,
        "total": total_count,
        "page": page,
        "pageSize": pageSize,
        "totalPages": total_pages
    }), 200


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
    current_user_id = int(get_jwt_identity())  # ✅ LOGGED-IN STAFF

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

@task_bp.route('/<int:task_id>/view', methods=['GET', 'POST'])
@jwt_required()
def view_task(task_id):
    user_id = int(get_jwt_identity())

    view = ComplaintView.query.filter_by(
        complaint_id=task_id,
        viewed_by=user_id
    ).first()

    if view:
        view.viewed_at = ist_dt()
    else:
        view = ComplaintView(
            complaint_id=task_id,
            viewed_by=user_id,
            viewed_at=ist_dt()
        )
        db.session.add(view)

    db.session.commit()

    user = User.query.get(user_id)

    return jsonify({
        "last_viewed_by": user.name if user else None,
        "last_viewed_at": view.viewed_at.isoformat()
    }), 200

    