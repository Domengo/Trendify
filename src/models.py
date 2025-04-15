from mongoengine import Document, StringField, DateTimeField, ReferenceField, IntField
import datetime


class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True, choices=['admin', 'influencer'])
    google_id = StringField()  # For Google OAuth


class Campaign(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    start_date = DateTimeField(default=datetime.datetime.now)
    end_date = DateTimeField()
    status = StringField(default='active', choices=[
        'active', 'completed', 'paused'])

    def to_mongo(self, use_db_field=True, fields=None):
        mongo_data = super().to_mongo(use_db_field, fields)
        if '_id' in mongo_data:
            mongo_data['_id'] = str(mongo_data['_id'])
        return mongo_data


class Submission(Document):
    influencer = ReferenceField(User, required=True)
    campaign = ReferenceField(Campaign, required=True)
    content_url = StringField(required=True)  # e.g., link to a post
    submission_date = DateTimeField(default=datetime.datetime.now)
    status = StringField(default='pending', choices=[
                         'pending', 'approved', 'rejected'])
    engagement_estimate = IntField(default=0)  # Estimated likes, shares, etc.
