from app.src.backend.directories.ClassificationDirector import ClassificationDirector
from app.src.backend.core.engine.BMModelFactory import BMModelFactory


class ClassificationFactory(BMModelFactory):

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    #----------------- Classification mlmodels -------------------#
    def create_classification_csv_model(self, request):
        return 0

    def create_classification_db_model(self, request):
        return 0

    def create_classification_gs_model(self, request):
        return 0

    def create_classification_sf_model(self, request):
        return 0

    def create_classification_text_model(self, request):
        classification_director = ClassificationDirector()
        return classification_director.create_text_classification_model(request)
    # ----------------- End Classification mlmodels -------------------#




