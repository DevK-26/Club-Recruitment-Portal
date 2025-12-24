"""API blueprint initialization"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import slots
