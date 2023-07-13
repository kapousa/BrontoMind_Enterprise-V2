from app.modules.base.app_routes.directors.dataprocessing.DataBotDirector import DataBotDirector


class DataBotFactory:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def build_dataset(self, request):
        databotdirector = DataBotDirector()
        return databotdirector.build_data_sheet(request)

    def process_bot_request(self, request):
        return 0