from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Job
from app.blueprints.auth.routes import role_required

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/create', methods=['POST'])
@role_required(['company'])  # Only company role allowed
def create_job():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    location = data.get('location')

    if not all([title, description]):
        return jsonify({"error": "Missing fields"}), 400

    user_id = get_jwt_identity()

    job = Job(
        title=title,
        description=description,
        location=location,
        created_by=user_id
    )
    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created", "job_id": job.id}), 201
