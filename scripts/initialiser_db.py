#!/usr/bin/env python3
"""
Script d'initialisation de la base de données Edusco
Crée les tables et insère des données de test
"""

import sys
import os
from datetime import datetime, date

# Ajouter le répertoire parent au path pour importer l'application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models.utilisateur import Utilisateur
from app.models.academique import (
    AnneeAcademique, Semestre, UniteEnseignement, Matiere,
    Etudiant, Enseignant, Groupe, InscriptionGroupe
)
from app.services.academique import ServiceAcademique
from app.services.authentification import ServiceAuthentification

def creer_donnees_test():
    """Crée des données de test pour l'application"""
    
    with app.app_context():
        print("🗄️  Initialisation de la base de données...")
        
        # Créer les tables
        db.create_all()
        print("✅ Tables créées avec succès")
        
        # Créer un administrateur par défaut
        print("👤 Création de l'administrateur par défaut...")
        admin, succes = ServiceAuthentification.creer_utilisateur(
            nom="Administrateur",
            prenom="Admin",
            email="admin@edusco.com",
            mot_de_passe="admin123",
            role="administrateur"
        )
        
        if succes:
            print("✅ Administrateur créé: admin@edusco.com / admin123")
        else:
            print("⚠️  L'administrateur existe déjà")
        
        # Créer une année académique
        print("📅 Création de l'année académique...")
        annee, succes = ServiceAcademique.creer_annee_academique(
            nom="2024-2025",
            date_debut=date(2024, 9, 1),
            date_fin=date(2025, 8, 31),
            active=True
        )
        
        if succes:
            print("✅ Année académique 2024-2025 créée")
        else:
            print("⚠️  L'année académique existe déjà")
            annee = ServiceAcademique.obtenir_annee_active()
        
        # Créer des semestres
        print("📚 Création des semestres...")
        semestres_data = [
            {
                "nom": "Semestre 1",
                "code": "S1",
                "date_debut": date(2024, 9, 1),
                "date_fin": date(2025, 1, 31),
                "actif": True
            },
            {
                "nom": "Semestre 2",
                "code": "S2",
                "date_debut": date(2025, 2, 1),
                "date_fin": date(2025, 6, 30),
                "actif": False
            }
        ]
        
        for semestre_data in semestres_data:
            semestre, succes = ServiceAcademique.creer_semestre(
                nom=semestre_data["nom"],
                code=semestre_data["code"],
                date_debut=semestre_data["date_debut"],
                date_fin=semestre_data["date_fin"],
                annee_id=annee.id,
                actif=semestre_data["actif"]
            )
            if succes:
                print(f"✅ Semestre {semestre.code} créé")
        
        # Récupérer le semestre actif
        semestre_actif = Semestre.query.filter_by(actif=True).first()
        
        # Créer des unités d'enseignement
        print("📖 Création des unités d'enseignement...")
        ues_data = [
            {
                "code": "UE101",
                "nom": "Mathématiques fondamentales",
                "description": "Introduction aux concepts mathématiques de base",
                "credits": 6,
                "coefficient": 2.0
            },
            {
                "code": "UE102",
                "nom": "Informatique générale",
                "description": "Bases de l'informatique et de la programmation",
                "credits": 4,
                "coefficient": 1.5
            },
            {
                "code": "UE103",
                "nom": "Langues et communication",
                "description": "Anglais technique et communication",
                "credits": 3,
                "coefficient": 1.0
            }
        ]
        
        for ue_data in ues_data:
            ue, succes = ServiceAcademique.creer_unite_enseignement(
                code=ue_data["code"],
                nom=ue_data["nom"],
                description=ue_data["description"],
                credits=ue_data["credits"],
                coefficient=ue_data["coefficient"],
                semestre_id=semestre_actif.id
            )
            if succes:
                print(f"✅ UE {ue.code} créée")
        
        # Créer des enseignants
        print("👨‍🏫 Création des enseignants...")
        enseignants_data = [
            {
                "matricule": "ENS001",
                "nom": "Dupont",
                "prenom": "Jean",
                "date_naissance": date(1980, 5, 15),
                "sexe": "M",
                "specialite": "Mathématiques",
                "grade": "Maître Assistant",
                "date_embauche": date(2010, 9, 1),
                "email": "jean.dupont@edusco.com",
                "telephone": "0123456789"
            },
            {
                "matricule": "ENS002",
                "nom": "Martin",
                "prenom": "Marie",
                "date_naissance": date(1985, 8, 22),
                "sexe": "F",
                "specialite": "Informatique",
                "grade": "Maître Assistant",
                "date_embauche": date(2012, 9, 1),
                "email": "marie.martin@edusco.com",
                "telephone": "0987654321"
            }
        ]
        
        for enseignant_data in enseignants_data:
            enseignant, succes = ServiceAcademique.creer_enseignant(
                matricule=enseignant_data["matricule"],
                nom=enseignant_data["nom"],
                prenom=enseignant_data["prenom"],
                date_naissance=enseignant_data["date_naissance"],
                sexe=enseignant_data["sexe"],
                specialite=enseignant_data["specialite"],
                grade=enseignant_data["grade"],
                date_embauche=enseignant_data["date_embauche"],
                email=enseignant_data["email"],
                telephone=enseignant_data["telephone"]
            )
            if succes:
                print(f"✅ Enseignant {enseignant.nom_complet} créé")
        
        # Créer des matières
        print("📚 Création des matières...")
        matieres_data = [
            {
                "code": "MAT101",
                "nom": "Algèbre linéaire",
                "description": "Vecteurs, matrices et systèmes d'équations",
                "volume_horaire": 60,
                "coefficient": 2.0,
                "ue_code": "UE101",
                "enseignant_matricule": "ENS001"
            },
            {
                "code": "MAT102",
                "nom": "Calcul différentiel",
                "description": "Dérivées et applications",
                "volume_horaire": 45,
                "coefficient": 1.5,
                "ue_code": "UE101",
                "enseignant_matricule": "ENS001"
            },
            {
                "code": "INF101",
                "nom": "Programmation Python",
                "description": "Introduction à la programmation avec Python",
                "volume_horaire": 75,
                "coefficient": 2.5,
                "ue_code": "UE102",
                "enseignant_matricule": "ENS002"
            },
            {
                "code": "ANG101",
                "nom": "Anglais technique",
                "description": "Anglais pour l'informatique",
                "volume_horaire": 30,
                "coefficient": 1.0,
                "ue_code": "UE103",
                "enseignant_matricule": None
            }
        ]
        
        for matiere_data in matieres_data:
            # Trouver l'UE
            ue = UniteEnseignement.query.filter_by(code=matiere_data["ue_code"]).first()
            
            # Trouver l'enseignant
            enseignant = None
            if matiere_data["enseignant_matricule"]:
                enseignant = Enseignant.query.filter_by(matricule=matiere_data["enseignant_matricule"]).first()
            
            matiere, succes = ServiceAcademique.creer_matiere(
                code=matiere_data["code"],
                nom=matiere_data["nom"],
                description=matiere_data["description"],
                volume_horaire=matiere_data["volume_horaire"],
                coefficient=matiere_data["coefficient"],
                ue_id=ue.id,
                enseignant_id=enseignant.id if enseignant else None
            )
            if succes:
                print(f"✅ Matière {matiere.code} créée")
        
        # Créer des étudiants
        print("👨‍🎓 Création des étudiants...")
        etudiants_data = [
            {
                "matricule": "2024-001",
                "nom": "Durand",
                "prenom": "Pierre",
                "date_naissance": date(2000, 3, 10),
                "sexe": "M",
                "email": "pierre.durand@student.edusco.com",
                "telephone": "0123456789"
            },
            {
                "matricule": "2024-002",
                "nom": "Leroy",
                "prenom": "Sophie",
                "date_naissance": date(2001, 7, 25),
                "sexe": "F",
                "email": "sophie.leroy@student.edusco.com",
                "telephone": "0987654321"
            },
            {
                "matricule": "2024-003",
                "nom": "Moreau",
                "prenom": "Thomas",
                "date_naissance": date(2000, 11, 5),
                "sexe": "M",
                "email": "thomas.moreau@student.edusco.com",
                "telephone": "0555666777"
            }
        ]
        
        for etudiant_data in etudiants_data:
            etudiant, succes = ServiceAcademique.creer_etudiant(
                matricule=etudiant_data["matricule"],
                nom=etudiant_data["nom"],
                prenom=etudiant_data["prenom"],
                date_naissance=etudiant_data["date_naissance"],
                sexe=etudiant_data["sexe"],
                email=etudiant_data["email"],
                telephone=etudiant_data["telephone"],
                annee_id=annee.id
            )
            if succes:
                print(f"✅ Étudiant {etudiant.nom_complet} créé")
        
        # Créer des groupes
        print("👥 Création des groupes...")
        groupes_data = [
            {
                "nom": "Groupe A",
                "code": "GA",
                "capacite_max": 20,
                "description": "Groupe principal",
                "ue_code": "UE101",
                "enseignant_matricule": "ENS001"
            },
            {
                "nom": "Groupe B",
                "code": "GB",
                "capacite_max": 15,
                "description": "Groupe secondaire",
                "ue_code": "UE102",
                "enseignant_matricule": "ENS002"
            }
        ]
        
        for groupe_data in groupes_data:
            # Trouver l'UE
            ue = UniteEnseignement.query.filter_by(code=groupe_data["ue_code"]).first()
            
            # Trouver l'enseignant
            enseignant = Enseignant.query.filter_by(matricule=groupe_data["enseignant_matricule"]).first()
            
            groupe, succes = ServiceAcademique.creer_groupe(
                nom=groupe_data["nom"],
                code=groupe_data["code"],
                capacite_max=groupe_data["capacite_max"],
                description=groupe_data["description"],
                ue_id=ue.id,
                enseignant_id=enseignant.id if enseignant else None
            )
            if succes:
                print(f"✅ Groupe {groupe.code} créé")
        
        # Inscrire des étudiants aux groupes
        print("📝 Inscription des étudiants aux groupes...")
        etudiants = Etudiant.query.all()
        groupes = Groupe.query.all()
        
        for i, etudiant in enumerate(etudiants):
            if i < len(groupes):
                succes = ServiceAcademique.inscrire_etudiant_groupe(
                    etudiant_id=etudiant.id,
                    groupe_id=groupes[i].id
                )
                if succes:
                    print(f"✅ {etudiant.nom_complet} inscrit au groupe {groupes[i].code}")
        
        print("\n🎉 Initialisation terminée avec succès!")
        print("\n📋 Récapitulatif:")
        print(f"   • {AnneeAcademique.query.count()} année(s) académique(s)")
        print(f"   • {Semestre.query.count()} semestre(s)")
        print(f"   • {UniteEnseignement.query.count()} unité(s) d'enseignement")
        print(f"   • {Matiere.query.count()} matière(s)")
        print(f"   • {Enseignant.query.count()} enseignant(s)")
        print(f"   • {Etudiant.query.count()} étudiant(s)")
        print(f"   • {Groupe.query.count()} groupe(s)")
        print(f"   • {Utilisateur.query.count()} utilisateur(s)")
        
        print("\n🔑 Identifiants de connexion:")
        print("   • Email: admin@edusco.com")
        print("   • Mot de passe: admin123")
        print("\n⚠️  N'oubliez pas de changer le mot de passe après la première connexion!")

if __name__ == "__main__":
    creer_donnees_test() 