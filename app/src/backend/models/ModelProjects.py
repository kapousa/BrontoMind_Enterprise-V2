# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import Column, Integer, String

from app import db


class ModelProjects(db.Model):

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    desc = Column(String)
    created_on = Column(String)
    updated_on = Column(String)
    created_date = Column(String)
    updated_date = Column(String)
    user_id = Column(Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)
        setattr(self, property, value)

    def __repr__(self):
        return str(self.model_id)



