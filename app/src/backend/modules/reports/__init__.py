from flask import Blueprint

blueprint = Blueprint(
    'reports_blueprint',
    __name__,
    url_prefix='/reports'
)