import logging

import numpy
from flask import render_template, session
from app.src.backend.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path
from app.src.backend.controllers.projects.ProjectsController import ProjectsController
from app.src.backend.directories.BaseDirector import BaseDirector


class ProjectsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def create_project(self, request):
        project_name = request.form.get('projectname')
        project_desc = request.form.get('description')
        user_id = session['logger']

        projects_controller = ProjectsController()
        add_projects = projects_controller.create_project(user_id, project_name, project_desc)

        return BaseDirector.load_home(request)

    def creatingthemodel(self, request, fname, ds_goal, ds_source):
        """
        Prepare the features and lablels before start creating the model
        @param request:
        @param fname:
        @param ds_goal:
        @param ds_source:
        @return:
        """
        predictionvalues = numpy.array((request.form.getlist('predcitedvalues')))
        featuresdvalues = numpy.array((request.form.getlist('featuresdvalues')))

        return render_template('applications/pages/prediction/creatingpredictionmodel.html',
                               predictionvalues=predictionvalues,
                               featuresdvalues=featuresdvalues,
                               progress_icon_path=progress_icon_path, fname=fname,
                               loading_icon_path=loading_icon_path,
                               ds_source=ds_source, ds_goal=ds_goal,
                               segment='createmodel')
