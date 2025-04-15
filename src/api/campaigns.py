from flask import Blueprint, request, jsonify
from src.models import Campaign
from src.auth import token_required, role_required

campaigns_bp = Blueprint('campaigns', __name__)


@campaigns_bp.route('/', methods=['GET'])
@token_required
def get_campaigns(current_user):
    """Get all campaigns (accessible to all authenticated users)."""
    campaigns = Campaign.objects().all()
    return jsonify([campaign.to_mongo() for campaign in campaigns]), 200


@campaigns_bp.route('/', methods=['POST'])
@token_required
@role_required('admin')
def create_campaign(current_user):
    """Create a new campaign (admin only)."""
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'description', 'start_date', 'end_date')):
        return jsonify({'message': 'Missing required fields'}), 400

    campaign = Campaign(**data)  # Assuming fields match the model
    campaign.save()
    return jsonify(campaign.to_mongo()), 201


@campaigns_bp.route('/<campaign_id>/performance', methods=['GET'])
@token_required
@role_required('admin')
def get_campaign_performance(current_user, campaign_id):
    """Get performance metrics for a specific campaign (admin only)."""

    return jsonify({'campaign_id': campaign_id, 'placeholder_metric': 100}), 200

# Additional endpoints (e.g., update campaign, delete campaign) can be added as needed
