"""
Blueprint d'authentification pour Edusco
Gère la connexion, déconnexion et la gestion des sessions
"""

from flask import Blueprint

bp = Blueprint('authentification', __name__)

from app.blueprints.authentification import routes 