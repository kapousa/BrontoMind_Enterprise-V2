import logging
import os.path

import numpy
from flask import render_template, session, abort, send_file, redirect, url_for
from app.src.backend.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path, my_datasets, \
    download_my_datasets
from app.src.backend.controllers.datasets.DatasetsController import DatasetsController
from app.src.backend.controllers.integrations.IntegrationsController import IntegrationsController
from app.src.backend.controllers.projects.ProjectsController import ProjectsController
from app.src.backend.directories.BaseDirector import BaseDirector
from app.src.backend.models.ModelIntegrationDetails import ModelIntegrationDetails
from app.src.backend.models.ModelIntegrations import ModelIntegrations
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets


class IntegrationsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def view_integrations(self):
        integration_controller = IntegrationsController()
        integrations = integration_controller.get_integrations(session['logger'])
        return render_template('/applications/pages/integrations/view.html', integrations=integrations,
                               segment='integrations', message=None)

    def select_integrator(self):
        return render_template('/applications/pages/integrations/selectintegrator.html', segment='integrations')

    def setup(self, integration_type):
        return render_template('/applications/pages/integrations/setup.html', integration_type=integration_type,
                               segment='integrations')

    def save(self, request, integration_type):
        try:
            form_inputs = request.form

            integration_controller = IntegrationsController()
            done = integration_controller.create_integration(integration_type, **form_inputs)
            message = 'Integration connection saved successfully' if done else ('Creating the integration connection '
                                                                                'failed, please try again.')
            integrations = integration_controller.get_integrations(session['logger'])

            return render_template('/applications/pages/integrations/view.html', ds_id=integration_type,
                                   integrations=integrations,
                                   segment='integrations', message=message)
        except Exception as e:
            print(e)
            logging.log(e, 'Error saving')
            return render_template('/applications/pages/integrations/view.html', ds_id=integration_type,
                                   segment='integrations', message='Integration connection failed')

    def refresh(self, integration_id, integration_type):
        try:
            intgeration_details = {}

            # Extracting connection parameters
            connection_info = ModelIntegrations.query.filter_by(id=integration_id).first()
            connection_params = ModelIntegrationDetails.query.filter_by(integration_id=integration_id).all()
            for connection_param in connection_params:
                intgeration_details[
                    connection_param.param_name] = connection_param.param_value if connection_param.param_value != '' else None
            intgeration_details['integration_name'] = connection_info.name
            intgeration_details['integration_id'] = integration_id
            integration_controller = IntegrationsController()
            done = integration_controller.refresh_integration_data(integration_type, **intgeration_details)
            message = 'Data form the integration connection refreshed successfully' if done else (
                'Refreshing the data from integration connection '
                'failed, please try again.')

            integrations = integration_controller.get_integrations(session['logger'])

            return render_template('/applications/pages/integrations/view.html', ds_id=integration_type,
                                   integrations=integrations,
                                   segment='integrations', message=message)
        except Exception as e:
            print(e)
            return render_template('/applications/pages/integrations/view.html', ds_id=integration_type,
                                   segment='integrations',
                                   message='Refreshing the data from integration connection '
                                           'failed, please try again.')
