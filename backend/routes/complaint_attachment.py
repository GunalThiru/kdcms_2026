import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.models import db
from backend.models.complaint_attachments import ComplaintAttachment

attachment_bp = Blueprint('attachments', __name__, url_prefix='/attachments')

UPLOAD_FOLDER = "uploads/complaints"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@attachment_bp.route("/upload/<int:complaint_id>", methods=["POST"])
def upload_attachment(complaint_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    saved_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(saved_path)

    attachment = ComplaintAttachment(
        complaint_id=complaint_id,
        filename=filename,
        file_path=saved_path,
        file_type=file.mimetype,
        file_size=os.path.getsize(saved_path)
    )

    db.session.add(attachment)
    db.session.commit()

    return jsonify({
        "message": "File uploaded",
        "attachment": attachment.to_dict()
    }), 201


@attachment_bp.route("/<int:id>", methods=["DELETE"])
def delete_attachment(id):
    attachment = ComplaintAttachment.query.get(id)
    if not attachment:
        return jsonify({"error": "Attachment not found"}), 404

    # delete file from disk
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    db.session.delete(attachment)
    db.session.commit()

    return jsonify({"message": "Attachment deleted"}), 200


@attachment_bp.route("/by-complaint/<int:complaint_id>", methods=["GET"])
def get_attachments(complaint_id):
    attachments = ComplaintAttachment.query.filter_by(complaint_id=complaint_id).all()
    return jsonify([a.to_dict() for a in attachments])
