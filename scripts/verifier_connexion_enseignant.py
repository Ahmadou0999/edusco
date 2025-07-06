#!/usr/bin/env python3
"""
Script pour vérifier et corriger le problème de connexion de l'enseignant Ousmane Ba
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models.utilisateur import Utilisateur
from app.models.academique import Enseignant
from app.services.authentification import ServiceAuthentification

def verifier_connexion_enseignant():
    """Vérifie et corrige le problème de connexion de l'enseignant Ousmane Ba"""
    
    with app.app_context():
        print("🔍 Vérification du problème de connexion de l'enseignant Ousmane Ba...")
        
        # 1. Vérifier si l'utilisateur existe
        email = "ousmane.ba@edusco.com"
        utilisateur = Utilisateur.query.filter_by(email=email).first()
        
        if not utilisateur:
            print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
            print("🔧 Création du compte utilisateur...")
            
            # Créer l'utilisateur
            utilisateur, succes = ServiceAuthentification.creer_utilisateur(
                nom="Ba",
                prenom="Ousmane",
                email=email,
                mot_de_passe="enseignant123",
                role='enseignant'
            )
            
            if succes:
                print(f"✅ Compte utilisateur créé pour {email}")
            else:
                print(f"❌ Erreur lors de la création du compte utilisateur")
                return
        else:
            print(f"✅ Utilisateur trouvé: {utilisateur.prenom} {utilisateur.nom}")
            print(f"   Email: {utilisateur.email}")
            print(f"   Rôle: {utilisateur.role}")
            print(f"   Actif: {utilisateur.actif}")
        
        # 2. Vérifier si l'enseignant existe
        enseignant = Enseignant.query.filter_by(email=email).first()
        
        if not enseignant:
            print(f"❌ Aucun enseignant trouvé avec l'email: {email}")
            print("🔧 Création du profil enseignant...")
            
            # Créer l'enseignant
            enseignant = Enseignant(
                matricule="ENS001",
                nom="Ba",
                prenom="Ousmane",
                date_naissance=datetime(1980, 1, 1).date(),
                sexe="M",
                specialite="Mathématiques",
                grade="Maître Assistant",
                telephone="+221 77 123 45 67",
                email=email,
                adresse="Dakar, Sénégal",
                date_embauche=datetime(2015, 9, 1).date(),
                utilisateur_id=utilisateur.id
            )
            
            db.session.add(enseignant)
            db.session.commit()
            print(f"✅ Profil enseignant créé pour {enseignant.nom_complet}")
        else:
            print(f"✅ Enseignant trouvé: {enseignant.nom_complet}")
            print(f"   Matricule: {enseignant.matricule}")
            print(f"   Spécialité: {enseignant.specialite}")
            
            # Vérifier si l'enseignant est lié à l'utilisateur
            if not enseignant.utilisateur_id:
                print("🔧 Liaison de l'enseignant à l'utilisateur...")
                enseignant.utilisateur_id = utilisateur.id
                db.session.commit()
                print("✅ Liaison effectuée")
        
        # 3. Réinitialiser le mot de passe avec bcrypt AVANT tout test
        print("\n🔧 Réinitialisation du mot de passe avec bcrypt...")
        from app.extensions import bcrypt
        utilisateur.mot_de_passe_hash = bcrypt.generate_password_hash("enseignant123").decode('utf-8')
        db.session.commit()
        print("✅ Mot de passe réinitialisé vers 'enseignant123' (bcrypt)")

        # 4. Tester la connexion avec le mot de passe du guide
        print("\n🔐 Test de connexion avec le mot de passe du guide...")
        utilisateur_test, succes = ServiceAuthentification.authentifier_utilisateur(
            email, "enseignant123"
        )
        if succes:
            print("✅ Connexion réussie avec 'enseignant123'")
        else:
            print("❌ Échec de connexion avec 'enseignant123'. Vérifiez la base de données.")

        # 5. Afficher les informations finales
        print("\n📋 Informations finales:")
        print(f"   • Email: {email}")
        print(f"   • Mot de passe: enseignant123")
        print(f"   • Rôle: {utilisateur.role}")
        print(f"   • Matricule: {enseignant.matricule}")
        print(f"   • Nom complet: {enseignant.nom_complet}")

        # 6. Tester la connexion finale
        print("\n🔐 Test de connexion finale...")
        utilisateur_final, succes_final = ServiceAuthentification.authentifier_utilisateur(
            email, "enseignant123"
        )
        if succes_final:
            print("✅ CONNEXION RÉUSSIE ! Le problème est résolu.")
            print("🎉 Vous pouvez maintenant vous connecter avec:")
            print(f"   Email: {email}")
            print(f"   Mot de passe: enseignant123")
        else:
            print("❌ PROBLÈME PERSISTANT. Vérifiez la base de données.")

if __name__ == "__main__":
    verifier_connexion_enseignant() 