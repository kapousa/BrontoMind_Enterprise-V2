import json

import numpy
from flask import request

from app.bck.bm.apis.v1.APIsPredictionServices import NpEncoder
from app.bck.bm.controllers.classification.ClassificationController import ClassificationController
from app.bck.bm.controllers.cvision.ObjectDetectionCotroller import ObjectDetectionCotroller
from app.bck.bm.db_helper.AttributesHelper import get_model_name, get_features, get_labels
from app.bck.bm.utiles.Helper import Helper


class APIsObjectDetectionServices:

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def label_files(self, content, model_id):
        testing_values = []
        features_list = get_features(model_id)
        labels_list = get_labels(model_id)

        run_identifier = "{}_{}".format(model_id, content['run_id'])
        desc = content['description']
        host= content['host']
        uname = content['username']
        pword = content['password']
        webcam = content['webcam']

        objectdetectioncotroller = ObjectDetectionCotroller()
        labeledfileslink, labeld = objectdetectioncotroller.labelfiles(run_identifier, desc, host, uname, pword, webcam, 28)

        # Create predicted values json object
        cluster_data_json = {
            "downloadlink": request.host_url + labeledfileslink
            }

        json_data = json.dumps(cluster_data_json, cls=NpEncoder)

        return json_data
