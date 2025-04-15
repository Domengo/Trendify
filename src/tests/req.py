import requests


def get_user_campaigns(jwt_token):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(
        "http://localhost:5000/api/campaigns/", headers=headers
    )  # Added trailing slash
    return response.json(), response.status_code


# ... rest of your code ...

print(get_user_campaigns(
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImRvbWVuZ28iLCJleHAiOjE3NDQ3NjExNzcsInJvbGUiOiJhZG1pbiJ9.Y3w9wSG9CqQLshrycExOPsGQ9Tka64WqffVD-bX-4bM"
))
