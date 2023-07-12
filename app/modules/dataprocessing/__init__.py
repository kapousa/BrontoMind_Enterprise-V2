from flask import Blueprint

blueprint = Blueprint(
    'dataprocessing_blueprint',
    __name__,
    url_prefix='/dataprocessing'
)