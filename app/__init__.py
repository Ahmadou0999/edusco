"""
Application Edusco - Plateforme de gestion d'institut supérieur
Initialisation de l'application Flask avec tous les blueprints et configurations
"""

from flask import Flask
from app.config import config
from app.extensions import initialiser_extensions, db
import os

def creer_application(config_name='default'):
    """
    Factory function pour créer l'application Flask
    
    Args:
        config_name: Nom de la configuration à utiliser
        
    Returns:
        Instance de l'application Flask configurée
    """
    
    # Création de l'application Flask
    app = Flask(__name__)
    
    # Configuration de l'application
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions
    initialiser_extensions(app)
    
    # Création du dossier uploads s'il n'existe pas
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Enregistrement des blueprints
    enregistrer_blueprints(app)
    
    # Création des tables de base de données
    with app.app_context():
        db.create_all()
    
    return app

def enregistrer_blueprints(app):
    """
    Enregistre tous les blueprints de l'application
    
    Args:
        app: Instance de l'application Flask
    """
    
    # Blueprint d'authentification
    from app.blueprints.authentification.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/authentification')
    
    # Blueprint d'administration
    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Blueprint enseignant
    from app.blueprints.enseignant import bp as enseignant_bp
    app.register_blueprint(enseignant_bp, url_prefix='/enseignant')
    
    # Blueprint étudiant
    from app.blueprints.etudiant import bp as etudiant_bp
    app.register_blueprint(etudiant_bp, url_prefix='/etudiant')
    
    # Blueprint principal (routes publiques)
    from app.blueprints.principal import bp as principal_bp
    app.register_blueprint(principal_bp)
    
    # Blueprint notifications
    from app.blueprints.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

# Création de l'application par défaut
app = creer_application() 