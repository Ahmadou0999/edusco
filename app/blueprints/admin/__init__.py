"""
Blueprint d'administration pour Edusco
Gère toutes les fonctionnalités administratives
"""

from flask import Blueprint

bp = Blueprint('admin', __name__)

from app.blueprints.admin import routes 