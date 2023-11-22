from app.src.backend.core.engine.BMModelFactory import BMModelFactory
from app.src.backend.directories import ForecastingDirector


class ForecastingFactory(BMModelFactory):

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    #----------------- Prediction mlmodels -------------------#
    def create_forecasting_csv_model(self, request):
        forecasting_director = ForecastingDirector()
        return forecasting_director.create_forecasting_model(request)

    def create_forecasting_db_model(self):
        return 0

    def create_forecasting_gs_model(self):
        return 0

    def create_forecasting_sf_model(self):
        return 0
    # ----------------- End prediction mlmodels -------------------#




