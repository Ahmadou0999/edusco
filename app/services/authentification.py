"""
Services d'authentification pour Edusco
Contient la logique métier pour l'authentification
"""

from flask_login import login_user, logout_user
from app.models.utilisateur import Utilisateur
from app.extensions import db
from datetime import datetime, timedelta
import secrets

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
                role=role,
                actif=True
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
                role='administrateur',
                actif=True
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Administrateur par défaut créé : admin@edusco.com / admin123")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'administrateur par défaut: {e}")
            return False
    
    @staticmethod
    def email_existe(email):
        """
        Vérifie si un email existe déjà dans la base de données
        
        Args:
            email (str): Email à vérifier
            
        Returns:
            bool: True si l'email existe déjà
        """
        return Utilisateur.query.filter_by(email=email).first() is not None
    
    @staticmethod
    def generer_token_reinitialisation(email):
        """
        Génère un token de réinitialisation pour un email
        
        Args:
            email (str): Email de l'utilisateur
            
        Returns:
            str: Token généré ou None si l'utilisateur n'existe pas
        """
        utilisateur = Utilisateur.query.filter_by(email=email).first()
        if not utilisateur:
            return None
        
        # Pour simplifier, on utilise un token basique
        # En production, il faudrait utiliser une bibliothèque comme itsdangerous
        token = secrets.token_urlsafe(32)
        
        # Stocker le token temporairement (en production, utiliser une table dédiée)
        utilisateur.token_reinitialisation = token
        utilisateur.token_expiration = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        
        return token
    
    @staticmethod
    def verifier_token_reinitialisation(token):
        """
        Vérifie la validité d'un token de réinitialisation
        
        Args:
            token (str): Token à vérifier
            
        Returns:
            Utilisateur: L'utilisateur associé au token ou None
        """
        utilisateur = Utilisateur.query.filter_by(token_reinitialisation=token).first()
        if not utilisateur:
            return None
        
        # Vérifier l'expiration
        if utilisateur.token_expiration and utilisateur.token_expiration < datetime.utcnow():
            return None
        
        return utilisateur
    
    @staticmethod
    def invalider_token_reinitialisation(token):
        """
        Invalide un token de réinitialisation
        
        Args:
            token (str): Token à invalider
        """
        utilisateur = Utilisateur.query.filter_by(token_reinitialisation=token).first()
        if utilisateur:
            utilisateur.token_reinitialisation = None
            utilisateur.token_expiration = None
            db.session.commit()
    
    @staticmethod
    def reinitialiser_mot_de_passe(utilisateur_id, nouveau_mot_de_passe):
        """
        Réinitialise le mot de passe d'un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            nouveau_mot_de_passe (str): Nouveau mot de passe
            
        Returns:
            bool: True si la réinitialisation a réussi
        """
        try:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return False
            
            utilisateur.mot_de_passe = nouveau_mot_de_passe
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la réinitialisation du mot de passe: {e}")
            return False
    
    @staticmethod
    def verifier_mot_de_passe(utilisateur_id, mot_de_passe):
        """
        Vérifie si un mot de passe correspond à un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            mot_de_passe (str): Mot de passe à vérifier
            
        Returns:
            bool: True si le mot de passe est correct
        """
        utilisateur = Utilisateur.query.get(utilisateur_id)
        if not utilisateur:
            return False
        
        return utilisateur.verifier_mot_de_passe(mot_de_passe)
    
    @staticmethod
    def verifier_email_avec_token(token):
        """
        Vérifie un email avec un token
        
        Args:
            token (str): Token de vérification
            
        Returns:
            Utilisateur: L'utilisateur vérifié ou None
        """
        utilisateur = Utilisateur.query.filter_by(token_verification_email=token).first()
        if not utilisateur:
            return None
        
        # Marquer l'email comme vérifié
        utilisateur.email_verifie = True
        utilisateur.token_verification_email = None
        db.session.commit()
        
        return utilisateur
    
    @staticmethod
    def renvoyer_email_verification(utilisateur_id):
        """
        Renvoie l'email de vérification
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            
        Returns:
            bool: True si l'email a été envoyé
        """
        # En production, implémenter l'envoi d'email
        # Pour l'instant, on simule
        return True
    
    @staticmethod
    def get_tous_utilisateurs():
        """
        Récupère tous les utilisateurs
        
        Returns:
            list: Liste de tous les utilisateurs
        """
        return Utilisateur.query.all()
    
    @staticmethod
    def activer_utilisateur(utilisateur_id):
        """
        Active un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            
        Returns:
            bool: True si l'activation a réussi
        """
        try:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return False
            
            utilisateur.actif = True
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'activation de l'utilisateur: {e}")
            return False
    
    @staticmethod
    def desactiver_utilisateur(utilisateur_id):
        """
        Désactive un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            
        Returns:
            bool: True si la désactivation a réussi
        """
        try:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return False
            
            utilisateur.actif = False
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la désactivation de l'utilisateur: {e}")
            return False
    
    @staticmethod
    def changer_role_utilisateur(utilisateur_id, nouveau_role):
        """
        Change le rôle d'un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            nouveau_role (str): Nouveau rôle
            
        Returns:
            bool: True si le changement a réussi
        """
        try:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return False
            
            utilisateur.role = nouveau_role
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du changement de rôle: {e}")
            return False
    
    @staticmethod
    def envoyer_email_reinitialisation(email, token):
        """
        Envoie un email de réinitialisation
        
        Args:
            email (str): Email de destination
            token (str): Token de réinitialisation
            
        Returns:
            bool: True si l'email a été envoyé
        """
        # En production, implémenter l'envoi d'email
        # Pour l'instant, on simule
        print(f"Email de réinitialisation envoyé à {email} avec le token: {token}")
        return True
    
    @staticmethod
    def creer_utilisateur_en_attente(nom, prenom, email, mot_de_passe, role='etudiant'):
        """
        Crée un utilisateur en attente de validation admin
        
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
            
            # Créer le nouvel utilisateur (inactif par défaut)
            nouvel_utilisateur = Utilisateur(
                nom=nom,
                prenom=prenom,
                email=email,
                mot_de_passe=mot_de_passe,
                role=role,
                actif=False
            )
            
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            
            return nouvel_utilisateur, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'utilisateur en attente: {e}")
            return None, False

    @staticmethod
    def notifier_admin_nouvelle_inscription(utilisateur):
        """
        Notifie les administrateurs d'une nouvelle inscription en attente
        
        Args:
            utilisateur: Instance de l'utilisateur en attente
        """
        try:
            # Récupérer tous les administrateurs
            admins = Utilisateur.query.filter_by(role='admin', actif=True).all()
            
            for admin in admins:
                # Créer une notification pour chaque admin
                notification = Notification(
                    utilisateur_id=admin.id,
                    titre="Nouvelle inscription en attente",
                    message=f"Un nouvel utilisateur ({utilisateur.nom} {utilisateur.prenom}) attend d'être validé. Email: {utilisateur.email}"
                )
                db.session.add(notification)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Erreur lors de la notification admin: {e}")

    @staticmethod
    def creer_invitation(email, role, expire_dans=7):
        """
        Crée une invitation pour un utilisateur
        
        Args:
            email (str): Email de l'invitation
            role (str): Rôle de l'utilisateur à créer
            expire_dans (int): Nombre de jours avant expiration
            
        Returns:
            str: Token d'invitation ou None si erreur
        """
        try:
            # Générer un token unique
            token = secrets.token_urlsafe(32)
            
            # Créer l'invitation (à implémenter avec un modèle Invitation)
            # Pour l'instant, on utilise une approche simple
            invitation_data = {
                'token': token,
                'email': email,
                'role': role,
                'expire_le': datetime.utcnow() + timedelta(days=expire_dans),
                'utilisee': False
            }
            
            # Stocker l'invitation (idéalement dans une table Invitation)
            # Pour l'instant, on peut utiliser une session ou cache
            return token
            
        except Exception as e:
            print(f"Erreur lors de la création de l'invitation: {e}")
            return None

    @staticmethod
    def verifier_invitation(token):
        """
        Vérifie la validité d'une invitation
        
        Args:
            token (str): Token d'invitation
            
        Returns:
            dict: Données de l'invitation ou None si invalide
        """
        try:
            # Vérifier l'invitation (à implémenter avec un modèle Invitation)
            # Pour l'instant, retourner des données de test
            return {
                'email': 'invite@example.com',
                'role': 'enseignant',
                'expire_le': datetime.utcnow() + timedelta(days=1)
            }
        except Exception as e:
            print(f"Erreur lors de la vérification de l'invitation: {e}")
            return None

    @staticmethod
    def creer_utilisateur_avec_invitation(nom, prenom, email, mot_de_passe, invitation):
        """
        Crée un utilisateur avec une invitation valide
        
        Args:
            nom (str): Nom de l'utilisateur
            prenom (str): Prénom de l'utilisateur
            email (str): Email de l'utilisateur
            mot_de_passe (str): Mot de passe en clair
            invitation (dict): Données de l'invitation
            
        Returns:
            tuple: (utilisateur, bool) - L'utilisateur créé et True si succès
        """
        try:
            # Vérifier si l'email existe déjà
            if Utilisateur.query.filter_by(email=email).first():
                return None, False
            
            # Créer le nouvel utilisateur avec le rôle de l'invitation
            nouvel_utilisateur = Utilisateur(
                nom=nom,
                prenom=prenom,
                email=email,
                mot_de_passe=mot_de_passe,
                role=invitation.get('role', 'etudiant'),
                actif=True
            )
            
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            
            return nouvel_utilisateur, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'utilisateur avec invitation: {e}")
            return None, False

    @staticmethod
    def utiliser_invitation(token):
        """
        Marque une invitation comme utilisée
        
        Args:
            token (str): Token de l'invitation
        """
        try:
            # Marquer l'invitation comme utilisée (à implémenter)
            print(f"Invitation {token} marquée comme utilisée")
        except Exception as e:
            print(f"Erreur lors de l'utilisation de l'invitation: {e}")

    @staticmethod
    def valider_inscription_utilisateur(utilisateur_id):
        """
        Valide une inscription utilisateur en attente
        
        Args:
            utilisateur_id (int): ID de l'utilisateur à valider
            
        Returns:
            bool: True si validation réussie
        """
        try:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return False
            
            # Activer le compte
            utilisateur.actif = True
            
            # Envoyer email de confirmation
            # service_auth.envoyer_email_validation(utilisateur.email)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la validation de l'inscription: {e}")
            return False

    @staticmethod
    def rejeter_inscription_utilisateur(utilisateur_id, raison=""):
        """
        Rejette une inscription utilisateur en attente
        
        Args:
            utilisateur_id (int): ID de l'utilisateur à rejeter
            raison (str): Raison du rejet
            
        Returns:
            bool: True si rejet réussi
        """
        try:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return False
            
            # Envoyer email de rejet
            # service_auth.envoyer_email_rejet(utilisateur.email, raison)
            
            # Supprimer l'utilisateur
            db.session.delete(utilisateur)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du rejet de l'inscription: {e}")
            return False 