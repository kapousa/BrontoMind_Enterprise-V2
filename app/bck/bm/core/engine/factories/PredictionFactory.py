from app.modules.base.app_routes.directors.PredictionDirector import PredictionDirector
from app.bck.bm.core.engine.BMModelFactory import BMModelFactory


class PredictionFactory(BMModelFactory):

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    #----------------- Prediction models -------------------#
    def create_prediction_csv_model(self, request):
        prediction_director = PredictionDirector()

        return prediction_director.complete_the_model(request)

    def create_prediction_db_model(self):
        return 0

    def create_prediction_gs_model(self):
        return 0

    def create_prediction_sf_model(self):
        return 0
    # ----------------- End prediction models -------------------#




