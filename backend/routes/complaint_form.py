from unittest import result
import pytz
from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from backend.models import db, Complaint, ComplaintAttachment
from backend.models.complaint_status_master import ComplaintStatus
from datetime import datetime
from werkzeug.utils import secure_filename
import os, json
from pathlib import Path
from sqlalchemy import or_,cast
from sqlalchemy.types import String
from backend.models.complaints import PROBLEM_TYPE_CODE
from backend.models.users import User
from sqlalchemy import func 
from sqlalchemy.orm import aliased
from backend.extensions import db
from backend.models.registered_by_type_master import RegisteredByTypeMaster
from backend.utils.complaint_email_notifier import notify_on_complaint_submission
from backend.services.sms_service import send_sms
from threading import Thread

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
    
        
    guest_type = RegisteredByTypeMaster.query.filter_by(code='guest').first()
    customer_type = RegisteredByTypeMaster.query.filter_by(code='customer').first()
    staff_type = RegisteredByTypeMaster.query.filter_by(code='staff').first()

    registered_by_type_id = None
    is_guest = False
    guest_mobile = None
    guest_email = None
    reporter_name = None



    # CASE 1: GUEST
    if not reported_by:
        registered_by_type_id = guest_type.id
        is_guest = True
        guest_mobile = data.get("guest_mobile")
        guest_email = data.get("guest_email")

        if not guest_mobile or not guest_mobile.isdigit() or len(guest_mobile) != 10:
            return jsonify({"error": "Valid guest mobile number is required"}), 400

        if not guest_email:
            return jsonify({"error": "Guest email is required"}), 400


    # CASE 2: CUSTOMER LOGIN
    elif data.get("registered_mode") == "customer":
        registered_by_type_id = customer_type.id
        is_guest = False

    # CASE 3: STAFF REGISTERING FOR CUSTOMER
    elif data.get("registered_mode") == "staff":
        registered_by_type_id = staff_type.id
        is_guest = False
        guest_mobile = data.get("customer_mobile")



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
        guest_mobile=guest_mobile,
        guest_email=guest_email,



        registered_by_type_id=registered_by_type_id,

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

    # 🔔 Send email in background (don't block response)
    
    # email_thread = Thread(target=notify_on_complaint_submission, args=(complaint,))
    # email_thread.daemon = True
    # email_thread.start()

    app = current_app._get_current_object()

    def run_email(complaint_id):
        with app.app_context():
            notify_on_complaint_submission(
                Complaint.query.get(complaint_id)
            )

    email_thread = Thread(
        target=run_email,
        args=(complaint.id,)
    )
    email_thread.daemon = True
    email_thread.start()
    





    # generating complaint no
    problem_code = PROBLEM_TYPE_CODE.get(complaint.problem_type, "OTH")

    #YEAR SUFFIX AND ZERO PAD TO 6 DIGITS
    year_suffix = ist_now.strftime("%y")   # 26
    running_id = str(complaint.id).zfill(6)


    complaint.complaint_no = f"CMP{problem_code}{year_suffix}{running_id}"
    
    sms_mobile = get_sms_mobile(complaint)
    if sms_mobile:
        sms_message = (
            f"Your complaint has been registered successfully. "
            f"Complaint No: {complaint.complaint_no}. "
            f"KTC"
        )
        current_app.logger.warning(
             f"SMS DEBUG → type={complaint.registered_by_type.code if complaint.registered_by_type else None}, "
             f"guest_mobile={complaint.guest_mobile}, "
            f"reported_by={complaint.reported_by}"
        )

        send_sms(sms_mobile, sms_message)
        print("SMS MOBILE:", sms_mobile)
        print("SMS MESSAGE:", sms_message)



    

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
        "complaint_no": complaint.complaint_no,
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

    # 🚫 DO NOT allow resolved fields here
    complaint.resolved_by = None
    complaint.solution_date_time = None


    db.session.commit()

    return jsonify({
        "message": "Complaint saved as in-progress",
        "complaint_id": complaint.id,
        "complaint_no": complaint.complaint_no
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
# -------------------------
# FILTERED COMPLAINTS LIST
# -------------------------

@complaint_bp.route('/list', methods=['GET'])
def list_complaints():

    # ---------- PAGINATION PARAMS ----------
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    offset = (page - 1) * page_size

    # ---------- FILTER PARAMS ----------
    status_code = request.args.get("status")
    problem_type = request.args.get("problem_type")
    sub_problem_type = request.args.get("sub_problem_type")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    search = request.args.get("search")

    resolver = aliased(User)

    query = db.session.query(
        Complaint,
        resolver.name.label("resolver_name")
    ).outerjoin(
        resolver,
        Complaint.resolved_by == resolver.id
    )

    # ---------- STATUS ----------
    if status_code:
        query = query.join(ComplaintStatus).filter(ComplaintStatus.code == status_code)

    # ---------- PROBLEM ----------
    if problem_type:
        query = query.filter(Complaint.problem_type == problem_type)

    if sub_problem_type:
        query = query.filter(Complaint.sub_problem_type == sub_problem_type)

    # ---------- DATE ----------
    if from_date:
        query = query.filter(
            Complaint.date_of_issue >= datetime.strptime(from_date, "%Y-%m-%d").date()
        )

    if to_date:
        query = query.filter(
            Complaint.date_of_issue <= datetime.strptime(to_date, "%Y-%m-%d").date()
        )

    # ---------- SEARCH ----------
    if search:
        search_like = f"%{search}%"
        query = (
            query
            .outerjoin(User, Complaint.reported_by == User.id)
            .filter(
                or_(
                    cast(Complaint.id, String).ilike(search_like),
                    User.name.ilike(search_like),
                    Complaint.reporter_name.ilike(search_like),
                    Complaint.problem_description.ilike(search_like),
                    Complaint.problem_type.ilike(search_like),
                    Complaint.sub_problem_type.ilike(search_like),
                    Complaint.reference_id.ilike(search_like),
                    Complaint.remarks.ilike(search_like),
                    Complaint.solution_provided.ilike(search_like)
                )
            )
        )

    # ---------- TOTAL COUNT (IMPORTANT) ----------
    total = query.count()

    # ---------- PAGINATED DATA ----------
    rows = (
        query
        .order_by(Complaint.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    data = []
    for complaint, resolved_by_name in rows:
        row = complaint.to_dict()
        row["resolved_by_name"] = resolved_by_name
        data.append(row)

    return jsonify({
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size
    }), 200




#track-complaint_bp
@complaint_bp.route('/track', methods=['POST'])
def track_complaint():
    data = request.get_json()

    complaint_no = data.get('complaint_no')
    reference_id = data.get('reference_id')

    if not complaint_no or not reference_id:
        return jsonify({'message': 'Invalid request'}), 400

    complaint = Complaint.query.filter_by(
        complaint_no=complaint_no,
        reference_id=reference_id
    ).first()

    if not complaint:
        return jsonify({'message': 'Not found'}), 404

    return jsonify({
        'complaint_id': complaint.id,
        'complaint_no': complaint.complaint_no,
        'status': complaint.status.code,
        'reference_type': complaint.reference_type,
        'reference_id': complaint.reference_id,
        'remarks': complaint.remarks,
        'solution_provided': complaint.solution_provided,
        'solution_date_time': complaint.solution_date_time.strftime('%d %b %Y %H:%M') if complaint.solution_date_time else None,
        'problem_type': complaint.problem_type,
        'sub_problem_type': complaint.sub_problem_type,

        'date_of_issue': complaint.date_of_issue.strftime('%d %b %Y'),
        'reporting_time': complaint.reporting_time.strftime('%H:%M'),
        'reported_by': complaint.reporter.name if complaint.reporter else complaint.reporter_name,
        'is_guest': complaint.is_guest, 
        'problem_description': complaint.problem_description,
        'created_at': complaint.created_at.strftime('%d %b %Y %H:%M'),  
        'guest_mobile': complaint.reference_id if complaint.is_guest and complaint.reference_type == 'mobile' else None,
        'guest_email': complaint.reference_id if complaint.is_guest and complaint.reference_type == 'email' else None,
        'remarks': complaint.remarks,
        'solution_provided': complaint.solution_provided,
        'resolved_by': complaint.resolver.name if complaint.resolver else None,
        'solution_date_time': complaint.solution_date_time.strftime('%d %b %Y %H:%M') if complaint.solution_date_time else None,
        # 'updated_at': complaint.updated_at.strftime('%d %b %Y %H:%M')
    })


@complaint_bp.route('/<int:complaint_id>/send-mail', methods=['POST'])
def send_complaint_mail(complaint_id):
    """Send email notification for a complaint"""
    try:
        from backend.services.mail_service import send_complaint_mail as send_mail
        
        result = send_mail(
            complaint_id=complaint_id,
            sent_by=request.json.get("sent_by") if request.json else None
        )
        return jsonify({"message": "Mail sent successfully", "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_sms_mobile(complaint):
    if not complaint.registered_by_type:
        return None

    code = complaint.registered_by_type.code

    if code == "guest":
        return complaint.guest_mobile

    if code == "customer":
        return complaint.reporter.mobile if complaint.reporter else None

    if code == "staff":
        return complaint.guest_mobile

    return None

    # Guest
    if complaint.registered_by_type.code == "guest":
        return complaint.guest_mobile

    # Customer login
    if complaint.registered_by_type.code == "customer":
        return complaint.reported_by.mobile if complaint.reported_by else None

    # Staff registering for customer
    if complaint.registered_by_type.code == "staff":
        return complaint.guest_mobile

    return None 