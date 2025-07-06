#!/usr/bin/env python3
"""
Script pour supprimer tous les enseignants et étudiants existants
Permet de recommencer à zéro avec une base de données propre
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models.utilisateur import Utilisateur
from app.models.academique import Enseignant, Etudiant
from app.models.pedagogique import Note, Absence, EmploiDuTemps
from app.models.academique import Groupe, Matiere, UniteEnseignement, Semestre, AnneeAcademique

def supprimer_donnees():
    """Supprime tous les enseignants et étudiants existants"""
    
    with app.app_context():
        print("🗑️  Suppression des données existantes...")
        
        # Compter les données avant suppression
        nb_enseignants = Enseignant.query.count()
        nb_etudiants = Etudiant.query.count()
        nb_utilisateurs = Utilisateur.query.filter(
            Utilisateur.role.in_(['enseignant', 'etudiant'])
        ).count()
        
        print(f"\n📊 Données à supprimer :")
        print(f"   • {nb_enseignants} enseignants")
        print(f"   • {nb_etudiants} étudiants") 
        print(f"   • {nb_utilisateurs} comptes utilisateurs (enseignants/étudiants)")
        
        # Demander confirmation
        confirmation = input("\n⚠️  ATTENTION : Cette action est irréversible !")
        confirmation += input("Êtes-vous sûr de vouloir supprimer toutes ces données ? (oui/non) : ")
        
        if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Suppression annulée.")
            return
        
        try:
            print("\n🔄 Suppression en cours...")
            
            # 1. Supprimer les données pédagogiques liées
            print("   • Suppression des notes...")
            Note.query.delete()
            
            print("   • Suppression des absences...")
            Absence.query.delete()
            
            print("   • Suppression des emplois du temps...")
            EmploiDuTemps.query.delete()
            
            # 2. Supprimer les groupes (qui contiennent des étudiants)
            print("   • Suppression des groupes...")
            Groupe.query.delete()
            
            # 3. Supprimer les matières (liées aux enseignants)
            print("   • Suppression des matières...")
            Matiere.query.delete()
            
            # 4. Supprimer les unités d'enseignement
            print("   • Suppression des unités d'enseignement...")
            UniteEnseignement.query.delete()
            
            # 5. Supprimer les semestres
            print("   • Suppression des semestres...")
            Semestre.query.delete()
            
            # 6. Supprimer les années académiques
            print("   • Suppression des années académiques...")
            AnneeAcademique.query.delete()
            
            # 7. Supprimer les étudiants
            print("   • Suppression des étudiants...")
            etudiants = Etudiant.query.all()
            for etudiant in etudiants:
                # Supprimer l'utilisateur associé s'il existe
                if etudiant.utilisateur:
                    db.session.delete(etudiant.utilisateur)
                db.session.delete(etudiant)
            
            # 8. Supprimer les enseignants
            print("   • Suppression des enseignants...")
            enseignants = Enseignant.query.all()
            for enseignant in enseignants:
                # Supprimer l'utilisateur associé s'il existe
                if enseignant.utilisateur:
                    db.session.delete(enseignant.utilisateur)
                db.session.delete(enseignant)
            
            # 9. Supprimer les utilisateurs restants avec rôles enseignant/étudiant
            print("   • Suppression des comptes utilisateurs restants...")
            utilisateurs_a_supprimer = Utilisateur.query.filter(
                Utilisateur.role.in_(['enseignant', 'etudiant'])
            ).all()
            
            for utilisateur in utilisateurs_a_supprimer:
                db.session.delete(utilisateur)
            
            # Valider toutes les suppressions
            db.session.commit()
            
            print("\n✅ Suppression terminée avec succès !")
            print("🎯 La base de données est maintenant prête pour un nouveau départ.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de la suppression : {str(e)}")
            print("🔄 Rollback effectué - aucune donnée n'a été supprimée.")

def afficher_statut():
    """Affiche le statut actuel de la base de données"""
    
    with app.app_context():
        print("📊 Statut actuel de la base de données :")
        print(f"   • Enseignants : {Enseignant.query.count()}")
        print(f"   • Étudiants : {Etudiant.query.count()}")
        print(f"   • Utilisateurs (enseignants/étudiants) : {Utilisateur.query.filter(Utilisateur.role.in_(['enseignant', 'etudiant'])).count()}")
        print(f"   • Années académiques : {AnneeAcademique.query.count()}")
        print(f"   • Semestres : {Semestre.query.count()}")
        print(f"   • Unités d'enseignement : {UniteEnseignement.query.count()}")
        print(f"   • Matières : {Matiere.query.count()}")
        print(f"   • Groupes : {Groupe.query.count()}")
        print(f"   • Notes : {Note.query.count()}")
        print(f"   • Absences : {Absence.query.count()}")

if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  SCRIPT DE SUPPRESSION DES DONNÉES")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--statut":
        afficher_statut()
    else:
        supprimer_donnees() 