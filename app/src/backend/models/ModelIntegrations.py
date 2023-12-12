# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import Column, Integer, String

from app import db


class ModelIntegrations(db.Model):

    __tablename__ = 'integrations'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)
    connection_string = Column(String)
    type = Column(Integer)
    user_id = Column(Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)
        setattr(self, property, value)

    def __repr__(self):
        return str(self.model_id)



