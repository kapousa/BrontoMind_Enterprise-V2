from flask import render_template


class CVisionDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    @staticmethod
    def select_cvision_type():
        return render_template('applications/pages/cvision/selectvision.html', message='There is no active model')



