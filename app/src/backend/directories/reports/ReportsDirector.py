from flask import render_template, session
from app.src.backend.controllers.reports.ReportsController import ReportsController


class ReportsDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def full_analyze(self, dataset_id, report_type=1):
        reports_controller = ReportsController()
        dataset_id, dataset, descriptive_report = reports_controller.get_full_analysis(
            session['logger'], dataset_id, report_type)
        return render_template('applications/pages/reports/quickreport.html', dataset_id=dataset_id, dataset=dataset,
                               descriptive_report=descriptive_report,
                               segment='datasets')

    def show_state_page(self, dataset_id):
        return render_template(f"applications/reports/{session['logger']}/{dataset_id}/stats.html")
