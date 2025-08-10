from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Job, User, JobStatus
from app.extensions import db
from app.blueprints.auth.routes import role_required  # role_required decorator you already have

jobs_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@jobs_bp.route('', methods=['POST'])
@role_required(['company'])
def create_job():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    title = data.get('title')
    description = data.get('description')
    location = data.get('location', '')
    status = data.get('status', 'Draft')

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    if status not in [s.value for s in JobStatus]:
        return jsonify({"error": "Invalid status"}), 400

    user_id = get_jwt_identity()
    job = Job(
        title=title,
        description=description,
        location=location,
        status=JobStatus(status),
        created_by=user_id
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created successfully", "job_id": job.id}), 201


@jobs_bp.route('/<job_id>', methods=['PUT'])
@role_required(['company'])
def update_job(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.created_by != user_id:
        return jsonify({"error": "Unauthorized to update this job"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    title = data.get('title')
    description = data.get('description')
    location = data.get('location')
    status = data.get('status')

    if title:
        job.title = title
    if description:
        job.description = description
    if location:
        job.location = location
    if status:
        if status not in [s.value for s in JobStatus]:
            return jsonify({"error": "Invalid status"}), 400
        job.status = JobStatus(status)

    db.session.commit()

    return jsonify({"message": "Job updated successfully"})


@jobs_bp.route('/<job_id>', methods=['DELETE'])
@role_required(['company'])
def delete_job(job_id):
    user_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.created_by != user_id:
        return jsonify({"error": "Unauthorized to delete this job"}), 403

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job deleted successfully"})


@jobs_bp.route('', methods=['GET'])
def list_jobs():
    # Optional filters: status, location, keyword in title/description
    status = request.args.get('status')
    location = request.args.get('location')
    keyword = request.args.get('keyword')

    query = Job.query.filter(Job.status != JobStatus.DRAFT)  # By default exclude drafts from listings

    if status:
        if status not in [s.value for s in JobStatus]:
            return jsonify({"error": "Invalid status filter"}), 400
        query = query.filter(Job.status == JobStatus(status))

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if keyword:
        query = query.filter(
            (Job.title.ilike(f"%{keyword}%")) | (Job.description.ilike(f"%{keyword}%"))
        )

    jobs = query.order_by(Job.created_at.desc()).all()

    jobs_list = [{
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "status": job.status.value,
        "created_by": job.created_by,
        "created_at": job.created_at.isoformat()
    } for job in jobs]

    return jsonify(jobs_list)


@jobs_bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    job_data = {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "status": job.status.value,
        "created_by": job.created_by,
        "created_at": job.created_at.isoformat()
    }

    return jsonify(job_data)
