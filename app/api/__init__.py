# -*- coding: utf-8 -*-

__author__ = 'yangyuenan'

from flask import Blueprint

api = Blueprint('api', __name__)

from . import putapi
