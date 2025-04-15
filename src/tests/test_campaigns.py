import unittest
from unittest.mock import patch, MagicMock
from src.api.campaigns import get_campaigns
from src.models import Campaign, User
from flask import Flask

@patch('src.models.Campaign.objects')
@patch('src.models.User.objects')
@patch('src.api.campaigns.token_required')  # Patch the decorator
class TestGetCampaigns(unittest.TestCase):

    def test_get_campaigns_success(self, mock_token_required, mock_user_objects, mock_campaign_objects):
        # Make the decorator do nothing
        mock_token_required.return_value = lambda f: f

        # Create some mock campaigns
        mock_campaign1 = MagicMock(spec=Campaign)
        mock_campaign1.to_mongo.return_value = {"_id": "1", "title": "Campaign 1"}
        mock_campaign2 = MagicMock(spec=Campaign)
        mock_campaign2.to_mongo.return_value = {"_id": "2", "title": "Campaign 2"}
        mock_campaigns = [mock_campaign1, mock_campaign2]

        # Configure the mock to return the mock campaigns
        mock_campaign_objects.return_value.all.return_value = mock_campaigns

        # Create a mock current_user (not needed anymore, but kept for clarity)
        mock_user = MagicMock(spec=User)

        # Create a Flask app for the test context
        app = Flask(__name__)

        # Create a test request context (no need to add headers now)
        with app.test_request_context():
            # Call the function within the context (don't pass mock_user directly)
            response, status_code = get_campaigns()  # get_campaigns no longer needs arguments

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0], {"_id": "1", "title": "Campaign 1"})
        self.assertEqual(response[1], {"_id": "2", "title": "Campaign 2"})

if __name__ == '__main__':
    unittest.main()
