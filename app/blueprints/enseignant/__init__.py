"""
Blueprint enseignant pour Edusco
Gère l'interface enseignant
"""

from flask import Blueprint

bp = Blueprint('enseignant', __name__)

from app.blueprints.enseignant import routes 