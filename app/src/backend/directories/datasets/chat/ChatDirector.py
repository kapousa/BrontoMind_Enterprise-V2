import logging
import os.path

import numpy
from flask import render_template, session, abort, send_file, redirect, url_for
from app.src.backend.constants.BM_CONSTANTS import progress_icon_path, loading_icon_path, my_datasets, \
    download_my_datasets
from app.src.backend.controllers.datasets.DatasetsController import DatasetsController
from app.src.backend.controllers.datasets.chat.ChatController import ChatController
from app.src.backend.controllers.projects.ProjectsController import ProjectsController
from app.src.backend.directories.BaseDirector import BaseDirector
from app.src.backend.models.ModelMyDatasets import ModelMyDatasets


class ChatDirector:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def start_chat(self, dataset_id):
        chat_controller = ChatController()
        dataset_file = chat_controller.start_chat(session['logger'], dataset_id)
        return render_template('/applications/pages/mydatasets/chat.html', dataset_file=dataset_file, segment='datasets')