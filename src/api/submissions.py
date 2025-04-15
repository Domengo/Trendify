from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import Submission, Campaign, User
from mongoengine.errors import DoesNotExist

submissions_bp = Blueprint('submissions', __name__, url_prefix='/submissions')

# Influencer: Submit content


@submissions_bp.route('', methods=['POST'])
@jwt_required()
def submit_content():
    current_user_id = get_jwt_identity()
    try:
        current_user = User.objects.get(id=current_user_id)
    except DoesNotExist:
        return jsonify({'msg': 'User not found'}), 404
    if current_user.role != 'influencer':
        return jsonify({'msg': 'Unauthorized'}), 403

    data = request.get_json()
    campaign_id = data.get('campaign_id')
    content_url = data.get('content_url')

    if not campaign_id or not content_url:
        return jsonify({'msg': 'Missing required fields'}), 400

    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except DoesNotExist:
        return jsonify({'msg': 'Campaign not found'}), 404

    submission = Submission(
        influencer=current_user,
        campaign=campaign,
        content_url=content_url,
        status='pending'
    ).save()

    return jsonify({'msg': 'Submission created', 'submission_id': str(submission.id)}), 201


# Influencer: View their submissions
@submissions_bp.route('', methods=['GET'])
@jwt_required()
def view_submissions():
    current_user_id = get_jwt_identity()
    try:
        current_user = User.objects.get(id=current_user_id)
    except DoesNotExist:
        return jsonify({'msg': 'User not found'}), 404
    if current_user.role != 'influencer':
        return jsonify({'msg': 'Unauthorized'}), 403

    submissions = Submission.objects(influencer=current_user)
    result = [{
        'id': str(s.id),
        'campaign': str(s.campaign.id),
        'content_url': s.content_url,
        'submission_date': s.submission_date,
        'status': s.status,
        'engagement_estimate': s.engagement_estimate
    } for s in submissions]

    return jsonify(result), 200


# Brand/SME: Approve/Reject submissions
@submissions_bp.route('/<submission_id>/status', methods=['PATCH'])
@jwt_required()
def update_submission_status(submission_id):
    current_user_id = get_jwt_identity()
    try:
        current_user = User.objects.get(id=current_user_id)
    except DoesNotExist:
        return jsonify({'msg': 'User not found'}), 404
    if current_user.role != 'admin':  # Assuming 'admin' role for brands/SMEs
        return jsonify({'msg': 'Unauthorized'}), 403

    try:
        submission = Submission.objects.get(id=submission_id)
    except DoesNotExist:
        return jsonify({'msg': 'Submission not found'}), 404

    data = request.get_json()
    new_status = data.get('status')  # Expecting 'approved' or 'rejected'

    if new_status not in ['approved', 'rejected']:
        return jsonify({'msg': 'Invalid status'}), 400

    submission.status = new_status
    submission.save()

    return jsonify({'msg': f'Submission {submission_id} {new_status}'}), 200
