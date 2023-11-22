from app.src.backend.directories.dataprocessing.DataProcessingDirector import DataProcessingDirector


class DataBotFactory:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def build_dataset(self, request):
        databotdirector = DataProcessingDirector()
        return databotdirector.build_data_sheet(request)

    def process_bot_request(self, request):
        return 0