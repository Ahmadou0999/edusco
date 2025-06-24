"""
Script d'initialisation de la base de données Edusco
Crée les tables et l'administrateur par défaut
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer l'application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from app.extensions import db
from app.services.authentification import ServiceAuthentification

def initialiser_base_de_donnees():
    """Initialise la base de données avec les tables et l'administrateur par défaut"""
    
    with app.app_context():
        print("🗄️  Création des tables de base de données...")
        
        # Créer toutes les tables
        db.create_all()
        print("✅ Tables créées avec succès !")
        
        print("👤 Création de l'administrateur par défaut...")
        
        # Créer l'administrateur par défaut
        if ServiceAuthentification.creer_administrateur_par_defaut():
            print("✅ Administrateur par défaut créé !")
            print("📧 Email: admin@edusco.com")
            print("🔑 Mot de passe: admin123")
            print("⚠️  IMPORTANT: Changez ces identifiants après la première connexion !")
        else:
            print("ℹ️  L'administrateur existe déjà ou une erreur s'est produite.")
        
        print("\n🎉 Initialisation terminée !")
        print("🚀 Vous pouvez maintenant lancer l'application avec: python app.py")

if __name__ == '__main__':
    initialiser_base_de_donnees() 