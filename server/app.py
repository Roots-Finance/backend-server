from flask import Blueprint, Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

api_router = Blueprint("api", __name__, url_prefix="/api", cli_group=None)

import server.api.account
import server.api.test
import server.api.user
import server.api.user.accounts
import server.api.user.budget
import server.api.user.budget.lessons
import server.api.user.cards
import server.api.user.portfolio
import server.api.user.portfolio.ai
import server.api.user.portfolio.preferences
import server.api.user.tax

app.register_blueprint(api_router)
