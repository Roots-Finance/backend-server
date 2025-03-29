from flask import Blueprint, Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

api_router = Blueprint("api", __name__, url_prefix="/api", cli_group=None)

import server.api.test
import server.api.user

app.register_blueprint(api_router)
