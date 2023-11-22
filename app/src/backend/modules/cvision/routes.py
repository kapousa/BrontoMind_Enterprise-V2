# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os

from flask import request, send_file
from flask_login import login_required

from app.src.backend.constants import results_path
from app.src.backend.modules.cvision import blueprint
from app.src.backend.controllers.BaseController import BaseController
from app.src.backend.core.engine.factories.CVisionFactory import CVisionFactory
from app.src.backend.core.engine.factories.cvision.FaceDetectionFactory import FaceDetectionFactory
from app.src.backend.core.engine.factories.cvision.ObjectDetectionFactory import ObjectDetectionFactory


## CVision

@blueprint.route('/selectvision', methods=['GET', 'POST'])
@login_required
def selectvision():
    cvisionfactory = CVisionFactory()
    return cvisionfactory.selectcvisiontype(request)

##---------Object Detection---------##
@blueprint.route('/createmodel/objectdetection', methods=['GET', 'POST'])
@login_required
def createobjectdetection():
    objectdetectionfactory = ObjectDetectionFactory()
    return objectdetectionfactory.createomodel(request)

@blueprint.route('<model_id>/showobjdetectemodel', methods=['GET', 'POST'])
@login_required
def showobjdetectemodel(model_id):
    profile = BaseController.get_model_status(model_id)
    objectdetectionfactory = ObjectDetectionFactory()

    return objectdetectionfactory.showmodeldashboard(profile)

@blueprint.route('<model_id>/objtdetect/detect', methods=['GET', 'POST'])
@login_required
def detect(model_id):
    objectdetectionfactory = ObjectDetectionFactory()
    return objectdetectionfactory.detectobjects(model_id, request)

@blueprint.route('<model_id>/<run_id>/downloadresults', methods=['GET', 'POST'])
def downloadresults(model_id, run_id):
    f = '{0}_{1}{2}'.format(model_id, run_id, '.zip')
    path = os.path.join(results_path, f)
    return send_file(path, as_attachment=True)


##---------Face Detection---------##
@blueprint.route('/createmodel/facedetection', methods=['GET', 'POST'])
@login_required
def createfacedetection():
    facedetectionfactory = FaceDetectionFactory()
    return facedetectionfactory.createmodel(request)

