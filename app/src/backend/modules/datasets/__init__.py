from flask import Blueprint

blueprint = Blueprint(
    'datasets_blueprint',
    __name__,
    url_prefix='/datasets'
)