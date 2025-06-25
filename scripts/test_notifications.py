#!/usr/bin/env python3
"""
Script de test pour le système de notifications
Teste l'envoi d'emails et la création de notifications
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import creer_application
from app.extensions import db, mail
from app.models.utilisateur import Utilisateur
from app.models.academique import Groupe
from app.services.notification import ServiceNotification

def test_notifications():
    """Test du système de notifications"""
    app = creer_application()
    
    with app.app_context():
        print("=== Test du système de notifications ===\n")
        
        # Récupérer un utilisateur de test
        utilisateur = Utilisateur.query.first()
        if not utilisateur:
            print("❌ Aucun utilisateur trouvé dans la base de données")
            return
        
        print(f"✅ Utilisateur de test: {utilisateur.nom} {utilisateur.prenom}")
        
        # Test 1: Création d'une notification simple
        print("\n1. Test de création d'une notification simple...")
        try:
            notif = ServiceNotification.creer_notification(
                utilisateur_id=utilisateur.id,
                titre="Test de notification",
                message="Ceci est un test du système de notifications.",
                envoyer_email=False
            )
            if notif:
                print("✅ Notification créée avec succès")
            else:
                print("❌ Échec de la création de la notification")
        except Exception as e:
            print(f"❌ Erreur lors de la création: {e}")
        
        # Test 2: Création d'une notification avec email
        print("\n2. Test de création d'une notification avec email...")
        try:
            notif = ServiceNotification.creer_notification(
                utilisateur_id=utilisateur.id,
                titre="Test de notification avec email",
                message="Ceci est un test du système de notifications avec envoi d'email.",
                envoyer_email=True
            )
            if notif:
                print("✅ Notification avec email créée avec succès")
            else:
                print("❌ Échec de la création de la notification avec email")
        except Exception as e:
            print(f"❌ Erreur lors de la création avec email: {e}")
        
        # Test 3: Notification globale
        print("\n3. Test de notification globale...")
        try:
            success = ServiceNotification.creer_notification_globale(
                titre="Annonce importante",
                message="Ceci est une annonce importante pour tous les utilisateurs.",
                envoyer_email=False
            )
            if success:
                print("✅ Notification globale créée avec succès")
            else:
                print("❌ Échec de la création de la notification globale")
        except Exception as e:
            print(f"❌ Erreur lors de la création globale: {e}")
        
        # Test 4: Notification par groupe
        print("\n4. Test de notification par groupe...")
        groupe = Groupe.query.first()
        if groupe:
            try:
                success = ServiceNotification.creer_notification_groupe(
                    groupe_id=groupe.id,
                    titre="Information pour le groupe",
                    message=f"Information importante pour le groupe {groupe.nom}.",
                    envoyer_email=False
                )
                if success:
                    print(f"✅ Notification pour le groupe {groupe.nom} créée avec succès")
                else:
                    print("❌ Échec de la création de la notification de groupe")
            except Exception as e:
                print(f"❌ Erreur lors de la création de groupe: {e}")
        else:
            print("⚠️  Aucun groupe trouvé pour le test")
        
        # Test 5: Marquer comme lue
        print("\n5. Test de marquage comme lue...")
        try:
            notifications = ServiceNotification.get_user_notifications(utilisateur.id)
            if notifications:
                notification = notifications[0]
                success = ServiceNotification.marquer_lue(notification.id, utilisateur.id)
                if success:
                    print("✅ Notification marquée comme lue")
                else:
                    print("❌ Échec du marquage comme lue")
            else:
                print("⚠️  Aucune notification trouvée pour le test")
        except Exception as e:
            print(f"❌ Erreur lors du marquage: {e}")
        
        # Test 6: Statistiques
        print("\n6. Statistiques des notifications...")
        try:
            total = ServiceNotification.get_all_notifications()
            non_lues = ServiceNotification.get_unread_notifications()
            print(f"✅ Total des notifications: {len(total)}")
            print(f"✅ Notifications non lues: {len(non_lues)}")
        except Exception as e:
            print(f"❌ Erreur lors du calcul des statistiques: {e}")
        
        print("\n=== Test terminé ===")

def test_email_configuration():
    """Test de la configuration email"""
    app = creer_application()
    
    with app.app_context():
        print("=== Test de la configuration email ===\n")
        
        # Vérifier la configuration
        print(f"Serveur SMTP: {app.config.get('MAIL_SERVER', 'Non configuré')}")
        print(f"Port SMTP: {app.config.get('MAIL_PORT', 'Non configuré')}")
        print(f"Utilisateur SMTP: {app.config.get('MAIL_USERNAME', 'Non configuré')}")
        print(f"TLS activé: {app.config.get('MAIL_USE_TLS', False)}")
        print(f"SSL activé: {app.config.get('MAIL_USE_SSL', False)}")
        
        # Test d'envoi d'email simple
        if app.config.get('MAIL_SERVER') and app.config.get('MAIL_USERNAME'):
            print("\nTest d'envoi d'email...")
            try:
                from flask_mail import Message
                
                msg = Message(
                    'Test Email - Edusco',
                    sender=app.config.get('MAIL_USERNAME'),
                    recipients=[app.config.get('MAIL_USERNAME')]  # Envoi à soi-même pour le test
                )
                msg.body = "Ceci est un test d'envoi d'email depuis Edusco."
                
                mail.send(msg)
                print("✅ Email envoyé avec succès")
            except Exception as e:
                print(f"❌ Erreur lors de l'envoi d'email: {e}")
        else:
            print("⚠️  Configuration email incomplète - test d'envoi ignoré")
        
        print("\n=== Test email terminé ===")

if __name__ == '__main__':
    print("Démarrage des tests de notifications...\n")
    
    # Test de la configuration email
    test_email_configuration()
    
    # Test du système de notifications
    test_notifications()
    
    print("\nTous les tests sont terminés !") 