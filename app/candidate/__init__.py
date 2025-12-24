"""Candidate blueprint initialization"""
from flask import Blueprint

candidate_bp = Blueprint('candidate', __name__)

from app.candidate import routes
