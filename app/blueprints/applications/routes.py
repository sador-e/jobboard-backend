from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Application, Job, User, ApplicationStatus
from app.extensions import db
from app.blueprints.auth.routes import role_required

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')


@applications_bp.route('', methods=['POST'])
@role_required(['applicant'])
def apply_job():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    job_id = data.get('job_id')
    resume_link = data.get('resume_link')
    cover_letter = data.get('cover_letter', '')

    if not job_id or not resume_link:
        return jsonify({"error": "job_id and resume_link are required"}), 400

    job = Job.query.get(job_id)
    if not job or job.status != JobStatus.OPEN:
        return jsonify({"error": "Job not found or not open for applications"}), 404

    user_id = get_jwt_identity()

    # Check if already applied to this job
    existing_app = Application.query.filter_by(applicant_id=user_id, job_id=job_id).first()
    if existing_app:
        return jsonify({"error": "Already applied to this job"}), 400

    application = Application(
        applicant_id=user_id,
        job_id=job_id,
        resume_link=resume_link,
        cover_letter=cover_letter
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Application submitted", "application_id": application.id}), 201


@applications_bp.route('/me', methods=['GET'])
@role_required(['applicant'])
def my_applications():
    user_id = get_jwt_identity()
    applications = Application.query.filter_by(applicant_id=user_id).all()

    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": app.job.title,
            "status": app.status.value,
            "applied_at": app.applied_at.isoformat(),
            "resume_link": app.resume_link,
            "cover_letter": app.cover_letter
        })

    return jsonify(result)


@applications_bp.route('/job/<job_id>', methods=['GET'])
@role_required(['company'])
def view_applications_for_job(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.created_by != user_id:
        return jsonify({"error": "Unauthorized to view applications for this job"}), 403

    applications = Application.query.filter_by(job_id=job_id).all()

    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "applicant_id": app.applicant_id,
            "applicant_name": app.applicant.name,
            "status": app.status.value,
            "applied_at": app.applied_at.isoformat(),
            "resume_link": app.resume_link,
            "cover_letter": app.cover_letter
        })

    return jsonify(result)


@applications_bp.route('/<application_id>', methods=['PUT'])
@role_required(['company'])
def update_application_status(application_id):
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Missing status field"}), 400

    new_status = data['status']
    if new_status not in [s.value for s in ApplicationStatus]:
        return jsonify({"error": "Invalid status"}), 400

    application = Application.query.get(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    user_id = get_jwt_identity()
    if application.job.created_by != user_id:
        return jsonify({"error": "Unauthorized to update this application"}), 403

    application.status = ApplicationStatus(new_status)
    db.session.commit()

    return jsonify({"message": "Application status updated"})


@applications_bp.route('/<application_id>', methods=['DELETE'])
@role_required(['applicant'])
def withdraw_application(application_id):
    user_id = get_jwt_identity()
    application = Application.query.get(application_id)

    if not application:
        return jsonify({"error": "Application not found"}), 404

    if application.applicant_id != user_id:
        return jsonify({"error": "Unauthorized to withdraw this application"}), 403

    db.session.delete(application)
    db.session.commit()

    return jsonify({"message": "Application withdrawn successfully"})
