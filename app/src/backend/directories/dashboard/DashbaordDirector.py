from flask import render_template, session
from app.src.backend.controllers.dashboard.DashboardController import DashboardController


class DashbaordDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def view_dashboard(self):
        dashboard_controller = DashboardController()
        dashboard_info = dashboard_controller.get_dashboard_info(session['logger'])
        return render_template("/applications/pages/dashboard/dashboard.html", dashboard_info=dashboard_info,
                               segment="dashboard")
