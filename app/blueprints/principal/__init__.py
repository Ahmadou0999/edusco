"""
Blueprint principal pour Edusco
Gère les routes publiques
"""

from flask import Blueprint

bp = Blueprint('principal', __name__)

from app.blueprints.principal import routes 