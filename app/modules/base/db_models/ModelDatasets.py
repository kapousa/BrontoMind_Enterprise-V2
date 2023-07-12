# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import Column, Integer, String

from app import db


class ModelDatasets(db.Model):

    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True, unique=True)
    file_name = Column(String)
    name = Column(String)
    desc = Column(String)
    type = Column(Integer)
    no_of_rows = Column(Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)
        setattr(self, property, value)

    def __repr__(self):
        return str(self.model_id)



