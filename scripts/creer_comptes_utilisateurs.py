#!/usr/bin/env python3
"""
Script pour créer des comptes utilisateurs pour les enseignants et étudiants existants
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models.utilisateur import Utilisateur
from app.models.academique import Enseignant, Etudiant
from app.services.authentification import ServiceAuthentification

def creer_comptes_utilisateurs():
    """Crée des comptes utilisateurs pour les enseignants et étudiants existants"""
    
    with app.app_context():
        print("🔐 Création des comptes utilisateurs...")
        
        # Créer des comptes pour les enseignants
        print("\n👨‍🏫 Création des comptes enseignants...")
        enseignants = Enseignant.query.all()
        
        for enseignant in enseignants:
            # Vérifier si l'enseignant a déjà un compte utilisateur
            if not enseignant.utilisateur_id:
                # Créer un email si l'enseignant n'en a pas
                if not enseignant.email:
                    email = f"{enseignant.prenom.lower()}.{enseignant.nom.lower()}@edusco.com"
                else:
                    email = enseignant.email
                
                # Créer le mot de passe (matricule + année)
                mot_de_passe = f"{enseignant.matricule}2024"
                
                # Créer le compte utilisateur
                utilisateur, succes = ServiceAuthentification.creer_utilisateur(
                    nom=enseignant.nom,
                    prenom=enseignant.prenom,
                    email=email,
                    mot_de_passe=mot_de_passe,
                    role='enseignant'
                )
                
                if succes:
                    # Lier l'utilisateur à l'enseignant
                    enseignant.utilisateur_id = utilisateur.id
                    db.session.commit()
                    print(f"✅ Compte créé pour {enseignant.nom_complet}")
                    print(f"   Email: {email}")
                    print(f"   Mot de passe: {mot_de_passe}")
                else:
                    print(f"❌ Erreur lors de la création du compte pour {enseignant.nom_complet}")
            else:
                print(f"ℹ️  {enseignant.nom_complet} a déjà un compte utilisateur")
        
        # Créer des comptes pour les étudiants
        print("\n👨‍🎓 Création des comptes étudiants...")
        etudiants = Etudiant.query.all()
        
        for etudiant in etudiants:
            # Vérifier si l'étudiant a déjà un compte utilisateur
            if not etudiant.utilisateur_id:
                # Créer un email si l'étudiant n'en a pas
                if not etudiant.email:
                    email = f"{etudiant.prenom.lower()}.{etudiant.nom.lower()}@student.edusco.com"
                else:
                    email = etudiant.email
                
                # Créer le mot de passe (matricule + année)
                mot_de_passe = f"{etudiant.matricule}2024"
                
                # Créer le compte utilisateur
                utilisateur, succes = ServiceAuthentification.creer_utilisateur(
                    nom=etudiant.nom,
                    prenom=etudiant.prenom,
                    email=email,
                    mot_de_passe=mot_de_passe,
                    role='etudiant'
                )
                
                if succes:
                    # Lier l'utilisateur à l'étudiant
                    etudiant.utilisateur_id = utilisateur.id
                    db.session.commit()
                    print(f"✅ Compte créé pour {etudiant.nom_complet}")
                    print(f"   Email: {email}")
                    print(f"   Mot de passe: {mot_de_passe}")
                else:
                    print(f"❌ Erreur lors de la création du compte pour {etudiant.nom_complet}")
            else:
                print(f"ℹ️  {etudiant.nom_complet} a déjà un compte utilisateur")
        
        # Afficher le récapitulatif
        print("\n📊 Récapitulatif des comptes utilisateurs:")
        total_utilisateurs = Utilisateur.query.count()
        enseignants_avec_compte = Enseignant.query.filter(Enseignant.utilisateur_id.isnot(None)).count()
        etudiants_avec_compte = Etudiant.query.filter(Etudiant.utilisateur_id.isnot(None)).count()
        
        print(f"   • Total utilisateurs: {total_utilisateurs}")
        print(f"   • Enseignants avec compte: {enseignants_avec_compte}")
        print(f"   • Étudiants avec compte: {etudiants_avec_compte}")
        
        print("\n🔑 Identifiants de connexion:")
        print("   • Admin: admin@edusco.com / admin123")
        
        # Afficher les identifiants des enseignants
        enseignants_avec_compte = Enseignant.query.filter(Enseignant.utilisateur_id.isnot(None)).all()
        if enseignants_avec_compte:
            print("\n👨‍🏫 Enseignants:")
            for enseignant in enseignants_avec_compte:
                utilisateur = Utilisateur.query.get(enseignant.utilisateur_id)
                print(f"   • {enseignant.nom_complet}: {utilisateur.email} / {enseignant.matricule}2024")
        
        # Afficher les identifiants des étudiants
        etudiants_avec_compte = Etudiant.query.filter(Etudiant.utilisateur_id.isnot(None)).all()
        if etudiants_avec_compte:
            print("\n👨‍🎓 Étudiants:")
            for etudiant in etudiants_avec_compte:
                utilisateur = Utilisateur.query.get(etudiant.utilisateur_id)
                print(f"   • {etudiant.nom_complet}: {utilisateur.email} / {etudiant.matricule}2024")

if __name__ == "__main__":
    creer_comptes_utilisateurs() 