from flask import Blueprint

blueprint = Blueprint(
    'projects_blueprint',
    __name__,
    url_prefix='/projects'
)