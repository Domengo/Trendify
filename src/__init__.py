from flask import Flask, jsonify
# from flask_mongoengine import MongoEngine
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os
from mongoengine import connect


def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = os.getenv(
                                            'JWT_SECRET_KEY',
                                            'your-secret-key'
                                            )

    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['MONGO_DBNAME'] = 'trendDB'
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

    # Replace with a strong secret key
    app.config['SECRET_KEY'] = app.config['JWT_SECRET_KEY']
    CORS(app)
    # Database
    # db = MongoEngine(app)
    connect(
        db=app.config['MONGO_DBNAME'],
        host=os.getenv('MONGO_URI', 'mongodb://localhost')
    )

    # Register blueprints
    from .api.auth import auth_bp
    from .api.campaigns import campaigns_bp
    from .api.submissions import submissions_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    @cross_origin()
    def health_check():
        try:
            from .models import User
            User.objects.first()  # Try to retrieve a document
            return jsonify(
                          {
                            'status': 'ok',
                            'message':
                            'Database connection successful'
                          }), 200
        except Exception as e:
            print(e)
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500


    print(app.url_map)

    return app
