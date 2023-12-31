# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import Column, Integer, String

from app import db


class ModelDashboardInfoView(db.Model):

    __tablename__ = 'dashboard_info'

    user_id = Column(Integer, primary_key=True, unique=True)
    datasets = Column(String)
    projects = Column(String)
    models = Column(String)
    integrations = Column(String)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)
        setattr(self, property, value)

    def __repr__(self):
        return str(self.model_id)



