"""
Extensions Flask pour l'application Edusco
Ce fichier centralise toutes les extensions utilisées dans l'application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def initialiser_extensions(app):
    """
    Initialise toutes les extensions Flask avec l'application
    
    Args:
        app: Instance de l'application Flask
    """
    
    # Configuration de SQLAlchemy
    db.init_app(app)
    
    # Configuration de Flask-Migrate
    migrate.init_app(app, db)
    
    # Configuration de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'authentification.connexion'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Configuration de Flask-Bcrypt
    bcrypt.init_app(app)
    
    # Configuration de Flask-Mail
    mail.init_app(app)
    
    # Configuration des callbacks pour Flask-Login
    from app.models.utilisateur import Utilisateur
    
    @login_manager.user_loader
    def charger_utilisateur(utilisateur_id):
        """Charge l'utilisateur pour Flask-Login"""
        return Utilisateur.query.get(int(utilisateur_id)) 