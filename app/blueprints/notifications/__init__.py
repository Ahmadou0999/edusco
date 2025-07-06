"""
Blueprint notifications pour Edusco
Gère les notifications système
"""

from flask import Blueprint

bp = Blueprint('notifications', __name__)

from app.blueprints.notifications import routes 