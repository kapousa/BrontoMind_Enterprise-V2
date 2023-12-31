import inspect
import logging

from flask import abort, session

from app.src.backend.constants.BM_CONSTANTS import DATA_SOURCE_TYPE_API
from app.src.backend.controllers.integrations.IntegrationsControllerHelper import IntegrationsControllerHelper
from app.src.backend.models.ModelIntegrations import ModelIntegrations
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets
from app.src.backend.utiles.Helper import Helper


class IntegrationsController:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def get_integrations(self, user_id):
        ''' Return all datasets of a user '''

        try:
            user_integrations = ModelIntegrations.query.filter_by(user_id=user_id).all()
            integrations = []
            for user_integration in user_integrations:
                user_mydataset = ModelMyDatasets.query.filter_by(integration_id=user_integration.id).first()
                integration_info = {
                    "id": user_integration.id,
                    "name": user_integration.name,
                    "type": user_integration.type,
                    "type_name": Helper.get_lookup_value(user_integration.type),
                    "description": user_integration.description,
                    "connection_string": user_integration.connection_string,
                    "mydataset_id": user_mydataset.id
                }
                integrations.append(integration_info)

            return integrations

        except Exception as e:
            logging.error(e)
            print(e)
            abort(500)

    def create_integration(self, connection_type, **connection_info):
        ''' Create the integration '''
        try:
            # Fetch data
            if connection_type == DATA_SOURCE_TYPE_API:
                df = IntegrationsControllerHelper.fetch_api_results(**connection_info)

            if df is None:
                return False

            # Save information of the integration
            saved_integration_id = IntegrationsControllerHelper.save_integration(connection_type, **connection_info)

            # Export data to my datasets
            export_to_mydataset = IntegrationsControllerHelper.export_to_mydataset(saved_integration_id,
                                                                                   connection_info.get(
                                                                                       'integration_name'), df,
                                                                                   connection_type, session['logger'])

            return True

        except Exception as e:
            frame = inspect.currentframe()
            method_name = frame.f_code.co_name
            err_msg = f"Error when call {method_name} method: {e}"
            print(err_msg)
            logging.error(err_msg)

            return False

    def refresh_integration_data(self, connection_type, **connection_info):
        ''' Refresh the data from the integration source '''
        try:
            # Fetch data
            if connection_type == DATA_SOURCE_TYPE_API:
                df = IntegrationsControllerHelper.fetch_api_results(**connection_info)

            if df is None:
                return False

            # Export data to my datasets
            export_to_mydataset = IntegrationsControllerHelper.export_to_mydataset(connection_info['integration_id'],
                                                                                   connection_info.get(
                                                                                       'integration_name'), df,
                                                                                   connection_type, session['logger'],
                                                                                   False)

            return True

        except Exception as e:
            frame = inspect.currentframe()
            method_name = frame.f_code.co_name
            err_msg = f"Error when call {method_name} method: {e}"
            print(err_msg)
            logging.error(err_msg)
