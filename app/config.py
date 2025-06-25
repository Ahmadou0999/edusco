import os
from dotenv import load_dotenv

# Charger les variables d'environnement seulement si le fichier .env existe
if os.path.exists('.env'):
    load_dotenv()

class Configuration:
    """Configuration de base pour l'application Edusco"""
    
    # Configuration generale
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cle-secrete-par-defaut-pour-developpement'
    APP_NAME = os.environ.get('APP_NAME', 'Edusco')
    APP_DESCRIPTION = os.environ.get('APP_DESCRIPTION', 'Plateforme de gestion d\'institut superieur')
    
    # Configuration de la base de donnees
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///edusco.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuration de l'application
    ITEMS_PAR_PAGE = 20  # Nombre d'elements par page pour la pagination
    UPLOAD_FOLDER = 'app/static/uploads'  # Dossier pour les fichiers uploades
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max pour les uploads
    
    # Configuration des roles
    ROLES = {
        'ADMIN': 'administrateur',
        'ENSEIGNANT': 'enseignant'
    }

class ConfigurationDeveloppement(Configuration):
    """Configuration pour l'environnement de developpement"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///edusco_dev.db'

class ConfigurationProduction(Configuration):
    """Configuration pour l'environnement de production"""
    DEBUG = False
    
class ConfigurationTest(Configuration):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///edusco_test.db'
    WTF_CSRF_ENABLED = False

# Configuration par defaut selon l'environnement
config = {
    'development': ConfigurationDeveloppement,
    'production': ConfigurationProduction,
    'testing': ConfigurationTest,
    'default': ConfigurationDeveloppement
} 