"""
Services d'authentification pour Edusco
Contient la logique métier pour l'authentification
"""

from flask_login import login_user, logout_user
from app.models.utilisateur import Utilisateur
from app.extensions import db
from datetime import datetime

class ServiceAuthentification:
    """Service pour gérer l'authentification des utilisateurs"""
    
    @staticmethod
    def authentifier_utilisateur(email, mot_de_passe):
        """
        Authentifie un utilisateur avec email et mot de passe
        
        Args:
            email (str): Email de l'utilisateur
            mot_de_passe (str): Mot de passe en clair
            
        Returns:
            tuple: (utilisateur, bool) - L'utilisateur et True si authentification réussie
        """
        utilisateur = Utilisateur.query.filter_by(email=email).first()
        
        if utilisateur and utilisateur.verifier_mot_de_passe(mot_de_passe):
            if utilisateur.actif:
                # Mettre à jour la dernière connexion
                utilisateur.derniere_connexion = datetime.utcnow()
                db.session.commit()
                return utilisateur, True
            else:
                return None, False
        return None, False
    
    @staticmethod
    def connecter_utilisateur(utilisateur, se_souvenir=False):
        """
        Connecte un utilisateur avec Flask-Login
        
        Args:
            utilisateur: Instance de l'utilisateur
            se_souvenir (bool): Si True, la session sera persistante
            
        Returns:
            bool: True si la connexion a réussi
        """
        try:
            login_user(utilisateur, remember=se_souvenir)
            return True
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False
    
    @staticmethod
    def deconnecter_utilisateur():
        """
        Déconnecte l'utilisateur actuel
        
        Returns:
            bool: True si la déconnexion a réussi
        """
        try:
            logout_user()
            return True
        except Exception as e:
            print(f"Erreur lors de la déconnexion: {e}")
            return False
    
    @staticmethod
    def creer_utilisateur(nom, prenom, email, mot_de_passe, role='enseignant'):
        """
        Crée un nouvel utilisateur
        
        Args:
            nom (str): Nom de l'utilisateur
            prenom (str): Prénom de l'utilisateur
            email (str): Email de l'utilisateur
            mot_de_passe (str): Mot de passe en clair
            role (str): Rôle de l'utilisateur
            
        Returns:
            tuple: (utilisateur, bool) - L'utilisateur créé et True si succès
        """
        try:
            # Vérifier si l'email existe déjà
            if Utilisateur.query.filter_by(email=email).first():
                return None, False
            
            # Créer le nouvel utilisateur
            nouvel_utilisateur = Utilisateur(
                nom=nom,
                prenom=prenom,
                email=email,
                mot_de_passe=mot_de_passe,
                role=role
            )
            
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            
            return nouvel_utilisateur, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            return None, False
    
    @staticmethod
    def changer_mot_de_passe(utilisateur, nouveau_mot_de_passe):
        """
        Change le mot de passe d'un utilisateur
        
        Args:
            utilisateur: Instance de l'utilisateur
            nouveau_mot_de_passe (str): Nouveau mot de passe en clair
            
        Returns:
            bool: True si le changement a réussi
        """
        try:
            utilisateur.mot_de_passe_hash = utilisateur.mot_de_passe_hash = \
                utilisateur.__class__.mot_de_passe_hash.property.columns[0].type.hash(nouveau_mot_de_passe)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du changement de mot de passe: {e}")
            return False
    
    @staticmethod
    def verifier_permissions(utilisateur, role_requis):
        """
        Vérifie si un utilisateur a les permissions nécessaires
        
        Args:
            utilisateur: Instance de l'utilisateur
            role_requis (str): Rôle requis pour l'action
            
        Returns:
            bool: True si l'utilisateur a les permissions
        """
        if not utilisateur or not utilisateur.actif:
            return False
        
        # Les administrateurs ont tous les droits
        if utilisateur.role == 'administrateur':
            return True
        
        # Vérifier le rôle spécifique
        return utilisateur.role == role_requis
    
    @staticmethod
    def creer_administrateur_par_defaut():
        """
        Crée un administrateur par défaut si aucun n'existe
        
        Returns:
            bool: True si l'administrateur a été créé ou existe déjà
        """
        try:
            # Vérifier si un administrateur existe déjà
            admin_existant = Utilisateur.query.filter_by(role='administrateur').first()
            if admin_existant:
                return True
            
            # Créer l'administrateur par défaut
            admin = Utilisateur(
                nom='Administrateur',
                prenom='Système',
                email='admin@edusco.com',
                mot_de_passe='admin123',
                role='administrateur'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Administrateur par défaut créé : admin@edusco.com / admin123")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'administrateur par défaut: {e}")
            return False 