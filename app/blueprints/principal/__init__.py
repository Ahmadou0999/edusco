"""
Blueprint principal pour Edusco
Gère les routes publiques
"""

from flask import Blueprint

bp = Blueprint('principal', __name__)

# Import des routes après la création du blueprint
from app.blueprints.principal import routes 