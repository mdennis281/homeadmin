from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_default_secret_key')

# Register blueprints
from blueprints.auth import auth_bp
from blueprints.api import api_bp
from blueprints.base import base_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(base_bp)

if __name__ == '__main__':
    app.run(debug=False)
