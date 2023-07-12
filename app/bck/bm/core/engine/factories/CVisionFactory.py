from flask import session

from app.modules.base.app_routes.directors import CVisionDirector


class CVisionFactory:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def selectcvisiontype(self, request):
        session['ds_goal'] = request.args.get("t")
        return CVisionDirector.select_cvision_type()