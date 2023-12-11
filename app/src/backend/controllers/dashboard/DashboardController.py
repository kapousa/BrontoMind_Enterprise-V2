import logging

from flask import abort

from app import db
from app.src.backend.constants.BM_CONSTANTS import DEVELOPMENT_PROJECT
from app.src.backend.models.ModelProjects import ModelProjects
from app.src.backend.models.views.ModelDashboardInfoView import ModelDashboardInfoView
from app.src.backend.utiles.Helper import Helper

from datetime import datetime

class DashboardController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def get_dashboard_info(self, user_id):
        try:
            modeldashboardinfoview = ModelDashboardInfoView.query.filter_by(user_id = user_id).first()

            return modeldashboardinfoview

        except Exception as e:
            print(e)
            logging.error(e)
            abort(500)
