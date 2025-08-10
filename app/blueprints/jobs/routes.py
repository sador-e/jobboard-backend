from flask import Blueprint

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/ping')
def ping():
    return "Jobs Blueprint Works!"