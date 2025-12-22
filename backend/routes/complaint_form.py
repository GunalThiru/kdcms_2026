import pytz
from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from backend.models import db, Complaint, ComplaintAttachment
from backend.models.complaint_status_master import ComplaintStatus
from datetime import datetime
from werkzeug.utils import secure_filename
import os, json
from pathlib import Path
from sqlalchemy import or_


complaint_bp = Blueprint('complaints', __name__, url_prefix='/complaints')

UPLOAD_FOLDER = "uploads/complaints"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load problem-subproblem map
json_path = Path(__file__).parent.parent / "data/problem_sub_problem_map.json"
with open(json_path) as f:
    PROBLEM_SUB_PROBLEM_MAP = json.load(f)

# -------------------------
# CREATE COMPLAINT (USER OR GUEST)
# -------------------------
@complaint_bp.route('', methods=['POST'])
def create_complaint():
    data = request.form

    status = ComplaintStatus.query.filter_by(code="PENDING").first()
    if not status:
        return jsonify({"error": "Complaint status not configured"}), 500

    ist = pytz.timezone("Asia/Kolkata")
    ist_now = datetime.now(ist).replace(tzinfo=None)

    reported_by = data.get("reported_by")
    is_guest = not reported_by

    complaint = Complaint(
        date_of_issue=ist_now.date(),
        reporting_time=ist_now.time(),
        reporting_mode="app",
        problem_type=data.get("problem_type"),
        sub_problem_type=data.get("sub_problem_type"),
        reference_type=data.get("reference_type"),
        reference_id=data.get("reference_id"),
        problem_description=data.get("problem_description"),

        # USER vs GUEST
        reported_by=int(reported_by) if reported_by else None,
        is_guest=is_guest,
        reporter_name=data.get("guest_name") if is_guest else None,
        

        solution_provided=data.get("solution_provided"),
        solution_date_time=(
            datetime.strptime(data.get("solution_date_time"), '%Y-%m-%d %H:%M:%S')
            if data.get("solution_date_time") else None
        ),
        resolved_by=int(data.get("resolved_by")) if data.get("resolved_by") else None,
        remarks=data.get("remarks"),
        status_id=status.id
    )

    db.session.add(complaint)
    db.session.commit()

    # -------------------------
    # SAVE ATTACHMENTS
    # -------------------------
    files = request.files.getlist("attachments")
    for file in files:
        if not file.filename:
            continue

        filename = secure_filename(file.filename)
        saved_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(saved_path)

        attachment = ComplaintAttachment(
            complaint_id=complaint.id,
            filename=filename,
            file_path=saved_path,
            file_type=file.mimetype,
            file_size=os.path.getsize(saved_path)
        )
        db.session.add(attachment)

    db.session.commit()

    return jsonify({
        "message": "Complaint created successfully",
        "id": complaint.id,
        "is_guest": is_guest
    }), 201


# -------------------------
# RESOLVE COMPLAINT
# -------------------------
@complaint_bp.route('/<int:complaint_id>/resolve', methods=['PUT'])
def resolve_complaint(complaint_id):
    data = request.json
    complaint = Complaint.query.get_or_404(complaint_id)
   

    status = ComplaintStatus.query.filter_by(code="COMPLETED").first()
    if not status:
        return jsonify({"error": "COMPLETED status not configured"}), 500

    solution_text = data.get("solution_provided")
    if not solution_text:
        return jsonify({"error": "Solution is required"}), 400

    complaint.solution_provided = solution_text
    complaint.solution_date_time = ist_dt()
    complaint.resolved_by = int(data.get("resolved_by")) if data.get("resolved_by") else None
    complaint.status_id = status.id

    db.session.commit()

    return jsonify({
        "message": "Complaint resolved successfully",
        "complaint_id": complaint.id
    }), 200


# -------------------------
# STAFF SAVE (IN PROGRESS)
# -------------------------
@complaint_bp.route('/<int:complaint_id>/staff-action', methods=['PUT'])
def save_staff_action(complaint_id):
    data = request.json
    complaint = Complaint.query.get_or_404(complaint_id)

    status = ComplaintStatus.query.filter_by(code="IN_PROGRESS").first()
    if not status:
        return jsonify({"error": "IN_PROGRESS status not configured"}), 500

    complaint.solution_provided = data.get("solution_provided")
    complaint.remarks = data.get("remarks")
    complaint.status_id = status.id

    db.session.commit()

    return jsonify({
        "message": "Complaint saved as in-progress",
        "complaint_id": complaint.id
    }), 200


# -------------------------
# STAFF TASKS (IMPORTANT FIX)
# -------------------------
@complaint_bp.route('/staff/tasks', methods=['GET'])
def get_staff_tasks():
    tasks = (
        db.session.query(Complaint)
        .outerjoin(ComplaintStatus)   # OUTER JOIN = guest-safe
        .filter(ComplaintStatus.code.in_(["PENDING", "IN_PROGRESS"]))
        .all()
    )

    return jsonify([c.to_dict(include_resolved_by=False) for c in tasks])


# -------------------------
# DOWNLOAD ATTACHMENT
# -------------------------
@complaint_bp.route('/uploads/complaints/<path:filename>', methods=['GET'])
def download_complaint_attachment(filename):

    upload_root = current_app.config.get(
        "UPLOAD_FOLDER",
        os.path.join(os.getcwd(), "uploads")
    )

    complaints_upload_dir = os.path.join(upload_root, "complaints")
    file_path = os.path.join(complaints_upload_dir, filename)

    if not os.path.exists(file_path):
        abort(404, description="File not found")

    return send_from_directory(
        complaints_upload_dir,
        filename,
        as_attachment=False
    )


# -------------------------
# MARK COMPLAINT IN PROGRESS (ON MODAL CLOSE)
# -------------------------
@complaint_bp.route('/<int:complaint_id>/in-progress', methods=['POST'])
def mark_complaint_in_progress(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)

    pending = ComplaintStatus.query.filter_by(code="PENDING").first()
    in_progress = ComplaintStatus.query.filter_by(code="IN_PROGRESS").first()

    if not pending or not in_progress:
        return jsonify({"error": "Status not configured"}), 500

    # ✅ Only update if still pending
    if complaint.status_id == pending.id:
        complaint.status_id = in_progress.id
        db.session.commit()

    return jsonify({"message": "Complaint marked as IN_PROGRESS"}), 200

# helper
def ist_dt():
    
    return datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)



# -------------------------
# COMPLAINTS SUMMARY
# -------------------------
@complaint_bp.route('/summary', methods=['GET'])
def complaint_summary():
    """
    Query params (optional):
    - from_date : YYYY-MM-DD
    - to_date   : YYYY-MM-DD
    """

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    query = db.session.query(Complaint)

    # -------------------------
    # DATE FILTER (DATE_OF_ISSUE)
    # -------------------------
    if from_date:
        query = query.filter(
            Complaint.date_of_issue >= datetime.strptime(from_date, "%Y-%m-%d").date()
        )

    if to_date:
        query = query.filter(
            Complaint.date_of_issue <= datetime.strptime(to_date, "%Y-%m-%d").date()
        )

    # -------------------------
    # STATUS COUNTS
    # -------------------------
    total = query.count()

    pending_count = query.join(ComplaintStatus).filter(
        ComplaintStatus.code == "PENDING"
    ).count()

    in_progress_count = query.join(ComplaintStatus).filter(
        ComplaintStatus.code == "IN_PROGRESS"
    ).count()

    completed_count = query.join(ComplaintStatus).filter(
        ComplaintStatus.code == "COMPLETED"
    ).count()

    return jsonify({
        "total": total,
        "pending": pending_count,
        "in_progress": in_progress_count,
        "completed": completed_count
    }), 200


# -------------------------
# FILTERED COMPLAINTS LIST
# -------------------------
@complaint_bp.route('/list', methods=['GET'])
def list_complaints():

    status_code = request.args.get("status")
    problem_type = request.args.get("problem_type")
    sub_problem_type = request.args.get("sub_problem_type")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    search = request.args.get("search")

    query = (
        db.session.query(Complaint)
        .join(ComplaintStatus)
    )

    # -------------------------
    # STATUS FILTER
    # -------------------------
    if status_code:
        query = query.filter(ComplaintStatus.code == status_code)

    # -------------------------
    # PROBLEM TYPE FILTER
    # -------------------------
    if problem_type:
        query = query.filter(Complaint.problem_type == problem_type)

    if sub_problem_type:
        query = query.filter(Complaint.sub_problem_type == sub_problem_type)

    # -------------------------
    # DATE RANGE FILTER
    # -------------------------
    if from_date:
        query = query.filter(
            Complaint.date_of_issue >= datetime.strptime(from_date, "%Y-%m-%d").date()
        )

    if to_date:
        query = query.filter(
            Complaint.date_of_issue <= datetime.strptime(to_date, "%Y-%m-%d").date()
        )

    # -------------------------
    # GLOBAL SEARCH (ALL FIELDS)
    # -------------------------
    if search:
        search_like = f"%{search}%"
        query = query.filter(
            or_(
                Complaint.problem_description.ilike(search_like),
                Complaint.problem_type.ilike(search_like),
                Complaint.sub_problem_type.ilike(search_like),
                Complaint.reference_id.ilike(search_like),
                Complaint.remarks.ilike(search_like),
                Complaint.solution_provided.ilike(search_like)
            )
        )


    complaints = query.order_by(Complaint.id.desc()).all()

    return jsonify([
        c.to_dict() for c in complaints
    ]), 200
