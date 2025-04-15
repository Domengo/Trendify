import unittest
from unittest.mock import patch, MagicMock
from src.auth import login
from src.models import User  # Import the User model

class TestLoginFunction(unittest.TestCase):

    @patch('src.auth.User')
    @patch('src.auth.check_password_hash')
    def test_successful_login(self, mock_check_password_hash, mock_user_model):
        mock_user = MagicMock(spec=User)  # Use spec to ensure correct attributes
        mock_user.username = "testuser"
        mock_user.password = "hashed_password"
        mock_user.role = "admin"  # Add the role attribute
        mock_user_model.objects.return_value.filter.return_value.first.return_value = mock_user
        mock_check_password_hash.return_value = True

        token = login("testuser", "password")
        self.assertIsNotNone(token)
        # You might want to decode the token and check its contents
        # (e.g., username, expiration, role) using the jwt library
        # But for a basic test, checking for non-None is sufficient.

    @patch('src.auth.User')
    @patch('src.auth.check_password_hash')
    def test_failed_login_invalid_credentials(self, mock_check_password_hash, mock_user_model):
        mock_user_model.objects.return_value.filter.return_value.first.return_value = None

        result = login("wronguser", "wrongpassword")
        self.assertIsNone(result)  # Assuming login returns None on failure

    @patch('src.auth.User')
    @patch('src.auth.check_password_hash')
    def test_failed_login_incorrect_password(self, mock_check_password_hash, mock_user_model):
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_user.password = "hashed_password"
        mock_user.role = "admin"
        mock_user_model.objects.return_value.filter.return_value.first.return_value = mock_user
        mock_check_password_hash.return_value = False  # Simulate incorrect password

        result = login("testuser", "wrongpassword")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
