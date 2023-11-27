import logging

from flask import abort

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.utiles.Helper import Helper

from datetime import datetime

class DatasetsController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def create_project(self, user_id, project_name, description):
        try:
            now = datetime.now()
            modelmodel = {'id': Helper.generate_id(),
                          'name': project_name,
                          'desc': description,
                          'created_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'created_by': user_id,
                          'updated_on': now.strftime("%d/%m/%Y %H:%M:%S"),
                          'updated_by': user_id,
                          'user_id': user_id,
                          'status': DEVELOPMENT_PROJECT}

            model_model = ModelProjects(**modelmodel)
            db.session.commit()
            # Add new profile
            db.session.add(model_model)
            db.session.commit()

            return modelmodel


        except Exception as e:
            db.session.rollback()
            logging.error(e)
            abort(500)
