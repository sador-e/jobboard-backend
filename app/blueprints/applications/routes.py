from flask import Blueprint

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/ping')
def ping():
    return "Applications Blueprint Works!"