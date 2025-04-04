from flask import Blueprint

api_blueprint = Blueprint('ai', __name__)

from . import handle_prompt