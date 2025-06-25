from app.extensions import db, mail
from app.models.utilisateur import Notification, Utilisateur
from app.models.academique import Groupe, Etudiant, InscriptionGroupe
from flask_mail import Message
from flask import url_for, current_app
from datetime import datetime

class ServiceNotification:
    """Service pour la gestion des notifications internes et emails"""

    @staticmethod
    def creer_notification(utilisateur_id, titre, message, envoyer_email=False, commit=True):
        """Créer une notification pour un utilisateur"""
        notif = Notification(
            utilisateur_id=utilisateur_id,
            titre=titre,
            message=message,
            lue=False,
            date_creation=datetime.utcnow()
        )
        db.session.add(notif)
        
        # Envoyer un email si demandé
        if envoyer_email:
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if utilisateur and utilisateur.email:
                ServiceNotification.envoyer_email(utilisateur, titre, message)
        
        if commit:
            db.session.commit()
        return notif

    @staticmethod
    def creer_notification_groupe(groupe_id, titre, message, envoyer_email=False):
        """Créer des notifications pour tous les étudiants d'un groupe"""
        groupe = Groupe.query.get(groupe_id)
        if not groupe:
            return False
        
        # Récupérer tous les étudiants du groupe via les inscriptions
        inscriptions = InscriptionGroupe.query.filter_by(groupe_id=groupe_id).all()
        
        for inscription in inscriptions:
            etudiant = inscription.etudiant
            # Vérifier si l'étudiant a un utilisateur associé
            if hasattr(etudiant, 'utilisateur') and etudiant.utilisateur:
                ServiceNotification.creer_notification(
                    utilisateur_id=etudiant.utilisateur.id,
                    titre=titre,
                    message=message,
                    envoyer_email=envoyer_email,
                    commit=False
                )
        
        db.session.commit()
        return True

    @staticmethod
    def creer_notification_globale(titre, message, envoyer_email=False):
        """Créer des notifications pour tous les utilisateurs"""
        utilisateurs = Utilisateur.query.all()
        
        for utilisateur in utilisateurs:
            ServiceNotification.creer_notification(
                utilisateur_id=utilisateur.id,
                titre=titre,
                message=message,
                envoyer_email=envoyer_email,
                commit=False
            )
        
        db.session.commit()
        return True

    @staticmethod
    def marquer_lue(notification_id, utilisateur_id=None):
        """Marquer une notification comme lue"""
        notif = Notification.query.get(notification_id)
        if notif:
            # Vérifier que l'utilisateur peut marquer cette notification
            if utilisateur_id and notif.utilisateur_id != utilisateur_id:
                return False
            
            notif.lue = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def supprimer_notification(notification_id, utilisateur_id=None):
        """Supprimer une notification"""
        notif = Notification.query.get(notification_id)
        if notif:
            # Vérifier que l'utilisateur peut supprimer cette notification
            if utilisateur_id and notif.utilisateur_id != utilisateur_id:
                return False
            
            db.session.delete(notif)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_notifications(utilisateur_id, limite=None):
        """Récupérer les notifications d'un utilisateur"""
        query = Notification.query.filter_by(utilisateur_id=utilisateur_id).order_by(Notification.date_creation.desc())
        if limite:
            query = query.limit(limite)
        return query.all()

    @staticmethod
    def get_all_notifications():
        """Récupérer toutes les notifications (pour admin)"""
        return Notification.query.order_by(Notification.date_creation.desc()).all()

    @staticmethod
    def get_unread_notifications():
        """Récupérer toutes les notifications non lues"""
        return Notification.query.filter_by(lue=False).order_by(Notification.date_creation.desc()).all()

    @staticmethod
    def envoyer_email(utilisateur: Utilisateur, sujet: str, body: str):
        """Envoyer un email à un utilisateur"""
        if not utilisateur.email:
            return False
        
        try:
            msg = Message(
                subject=sujet,
                recipients=[utilisateur.email],
                body=body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'envoi d'email: {e}")
            return False

    @staticmethod
    def notifier_et_email(utilisateur_id, titre, message, envoyer_email=True):
        """Créer une notification et envoyer un email"""
        return ServiceNotification.creer_notification(
            utilisateur_id=utilisateur_id,
            titre=titre,
            message=message,
            envoyer_email=envoyer_email
        ) 