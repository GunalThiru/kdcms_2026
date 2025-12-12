from flask import Blueprint, request, jsonify
from backend.models import db, Complaint, ComplaintAttachment
from datetime import datetime
import os, json
from werkzeug.utils import secure_filename
from pathlib import Path

complaint_bp = Blueprint('complaints', __name__, url_prefix='/complaints')

UPLOAD_FOLDER = "uploads/complaints"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load problem-subproblem map
json_path = Path(__file__).parent.parent / "data/problem_sub_problem_map.json"
with open(json_path) as f:
    PROBLEM_SUB_PROBLEM_MAP = json.load(f)


@complaint_bp.route('', methods=['POST'])
def create_complaint():
    data = request.form

    # reference_id = f"{data.get('problem_type')[:3].upper()}-{int(datetime.utcnow().timestamp())}"

    complaint = Complaint(
        date_of_issue=datetime.utcnow().date(),
        reporting_time=datetime.utcnow().time(),
        reporting_mode="app",
        problem_type=data.get("problem_type"),
        sub_problem_type=data.get("sub_problem_type"),
        reference_type=data.get("reference_type"),
        reference_id=data.get("reference_id"),
        problem_description=data.get("problem_description"),
        reported_by=1
    )

    db.session.add(complaint)
    db.session.commit()

    # Save attachments
    files = request.files.getlist("attachments")
    for file in files:
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

    return jsonify({"message": "Complaint created", "id": complaint.id}), 201
