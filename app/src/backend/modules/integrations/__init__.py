from flask import Blueprint

blueprint = Blueprint(
    'integrations_blueprint',
    __name__,
    url_prefix='/integrations'
)