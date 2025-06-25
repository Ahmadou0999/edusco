"""
Services pour la gestion académique Edusco
Contient la logique métier pour la gestion académique
"""

from app.extensions import db
from app.models.academique import (
    AnneeAcademique, Semestre, UniteEnseignement, Matiere,
    Etudiant, Enseignant, Groupe, InscriptionGroupe
)
from app.models.pedagogique import Note, Absence, EmploiDuTemps, Deliberation
from datetime import datetime, date
from typing import Tuple, List, Optional
import os

class ServiceAcademique:
    """Service pour la gestion académique"""
    
    # ==================== ANNÉES ACADÉMIQUES ====================
    
    @staticmethod
    def creer_annee_academique(nom: str, date_debut: date, date_fin: date, active: bool = False) -> Tuple[AnneeAcademique, bool]:
        """Crée une nouvelle année académique"""
        try:
            # Désactiver toutes les autres années si celle-ci est active
            if active:
                AnneeAcademique.query.update({'active': False})
            
            annee = AnneeAcademique(
                nom=nom,
                date_debut=date_debut,
                date_fin=date_fin,
                active=active
            )
            
            db.session.add(annee)
            db.session.commit()
            return annee, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_annee_active() -> Optional[AnneeAcademique]:
        """Obtient l'année académique active"""
        return AnneeAcademique.query.filter_by(active=True).first()
    
    @staticmethod
    def obtenir_toutes_annees() -> List[AnneeAcademique]:
        """Obtient toutes les années académiques"""
        return AnneeAcademique.query.order_by(AnneeAcademique.nom.desc()).all()
    
    @staticmethod
    def modifier_annee_academique(annee_id: int, nom: str, date_debut: date, date_fin: date, active: bool) -> bool:
        """Modifie une année académique"""
        try:
            annee = AnneeAcademique.query.get(annee_id)
            if not annee:
                return False
            
            # Désactiver toutes les autres années si celle-ci devient active
            if active:
                AnneeAcademique.query.filter(AnneeAcademique.id != annee_id).update({'active': False})
            
            annee.nom = nom
            annee.date_debut = date_debut
            annee.date_fin = date_fin
            annee.active = active
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    # ==================== SEMESTRES ====================
    
    @staticmethod
    def creer_semestre(nom: str, code: str, date_debut: date, date_fin: date, annee_id: int, actif: bool = False) -> Tuple[Semestre, bool]:
        """Crée un nouveau semestre"""
        try:
            # Désactiver tous les autres semestres si celui-ci est actif
            if actif:
                Semestre.query.filter_by(annee_academique_id=annee_id).update({'actif': False})
            
            semestre = Semestre(
                nom=nom,
                code=code,
                date_debut=date_debut,
                date_fin=date_fin,
                annee_academique_id=annee_id,
                actif=actif
            )
            
            db.session.add(semestre)
            db.session.commit()
            return semestre, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_semestres_par_annee(annee_id: int) -> List[Semestre]:
        """Obtient tous les semestres d'une année académique"""
        return Semestre.query.filter_by(annee_academique_id=annee_id).order_by(Semestre.code).all()
    
    # ==================== UNITÉS D'ENSEIGNEMENT ====================
    
    @staticmethod
    def creer_unite_enseignement(code: str, nom: str, description: str, credits: int, coefficient: float, semestre_id: int) -> Tuple[UniteEnseignement, bool]:
        """Crée une nouvelle unité d'enseignement"""
        try:
            ue = UniteEnseignement(
                code=code,
                nom=nom,
                description=description,
                credits=credits,
                coefficient=coefficient,
                semestre_id=semestre_id
            )
            
            db.session.add(ue)
            db.session.commit()
            return ue, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_ues_par_semestre(semestre_id: int) -> List[UniteEnseignement]:
        """Obtient toutes les UEs d'un semestre"""
        return UniteEnseignement.query.filter_by(semestre_id=semestre_id).order_by(UniteEnseignement.code).all()
    
    # ==================== MATIÈRES ====================
    
    @staticmethod
    def creer_matiere(code: str, nom: str, description: str, volume_horaire: int, coefficient: float, ue_id: int, enseignant_id: int = None) -> Tuple[Matiere, bool]:
        """Crée une nouvelle matière"""
        try:
            matiere = Matiere(
                code=code,
                nom=nom,
                description=description,
                volume_horaire=volume_horaire,
                coefficient=coefficient,
                unite_enseignement_id=ue_id,
                enseignant_id=enseignant_id
            )
            
            db.session.add(matiere)
            db.session.commit()
            return matiere, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_matieres_par_ue(ue_id: int) -> List[Matiere]:
        """Obtient toutes les matières d'une UE"""
        return Matiere.query.filter_by(unite_enseignement_id=ue_id).order_by(Matiere.code).all()
    
    @staticmethod
    def obtenir_matieres_par_enseignant(enseignant_id: int) -> List[Matiere]:
        """Obtient toutes les matières d'un enseignant"""
        return Matiere.query.filter_by(enseignant_id=enseignant_id).order_by(Matiere.code).all()
    
    # ==================== ÉTUDIANTS ====================
    
    @staticmethod
    def creer_etudiant(matricule: str, nom: str, prenom: str, date_naissance: date, sexe: str, 
                      lieu_naissance: str = None, adresse: str = None, telephone: str = None, 
                      email: str = None, annee_id: int = None) -> Tuple[Etudiant, bool]:
        """Crée un nouvel étudiant"""
        try:
            # Si aucune année n'est spécifiée, utiliser l'année active
            if not annee_id:
                annee_active = ServiceAcademique.obtenir_annee_active()
                if not annee_active:
                    return None, False
                annee_id = annee_active.id
            
            etudiant = Etudiant(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                lieu_naissance=lieu_naissance,
                sexe=sexe,
                adresse=adresse,
                telephone=telephone,
                email=email,
                annee_academique_id=annee_id
            )
            
            db.session.add(etudiant)
            db.session.commit()
            return etudiant, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_etudiants_par_annee(annee_id: int = None) -> List[Etudiant]:
        """Obtient tous les étudiants d'une année académique"""
        if not annee_id:
            annee_active = ServiceAcademique.obtenir_annee_active()
            if not annee_active:
                return []
            annee_id = annee_active.id
        
        return Etudiant.query.filter_by(annee_academique_id=annee_id).order_by(Etudiant.nom, Etudiant.prenom).all()
    
    @staticmethod
    def rechercher_etudiants(terme: str) -> List[Etudiant]:
        """Recherche des étudiants par nom, prénom ou matricule"""
        return Etudiant.query.filter(
            db.or_(
                Etudiant.nom.ilike(f'%{terme}%'),
                Etudiant.prenom.ilike(f'%{terme}%'),
                Etudiant.matricule.ilike(f'%{terme}%')
            )
        ).order_by(Etudiant.nom, Etudiant.prenom).all()
    
    # ==================== ENSEIGNANTS ====================
    
    @staticmethod
    def creer_enseignant(matricule: str, nom: str, prenom: str, date_naissance: date, sexe: str,
                        date_embauche: date, lieu_naissance: str = None, adresse: str = None,
                        telephone: str = None, email: str = None, specialite: str = None,
                        grade: str = None) -> Tuple[Enseignant, bool]:
        """Crée un nouvel enseignant"""
        try:
            enseignant = Enseignant(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                lieu_naissance=lieu_naissance,
                sexe=sexe,
                adresse=adresse,
                telephone=telephone,
                email=email,
                specialite=specialite,
                grade=grade,
                date_embauche=date_embauche
            )
            
            db.session.add(enseignant)
            db.session.commit()
            return enseignant, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_tous_enseignants() -> List[Enseignant]:
        """Obtient tous les enseignants"""
        return Enseignant.query.filter_by(statut='actif').order_by(Enseignant.nom, Enseignant.prenom).all()
    
    # ==================== GROUPES ====================
    
    @staticmethod
    def creer_groupe(nom: str, code: str, capacite_max: int, ue_id: int, 
                    enseignant_id: int = None, description: str = None) -> Tuple[Groupe, bool]:
        """Crée un nouveau groupe"""
        try:
            groupe = Groupe(
                nom=nom,
                code=code,
                capacite_max=capacite_max,
                description=description,
                enseignant_responsable_id=enseignant_id,
                unite_enseignement_id=ue_id
            )
            
            db.session.add(groupe)
            db.session.commit()
            return groupe, True
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def obtenir_groupes_par_ue(ue_id: int) -> List[Groupe]:
        """Obtient tous les groupes d'une UE"""
        return Groupe.query.filter_by(unite_enseignement_id=ue_id).order_by(Groupe.code).all()
    
    @staticmethod
    def inscrire_etudiant_groupe(etudiant_id: int, groupe_id: int) -> bool:
        """Inscrit un étudiant à un groupe"""
        try:
            # Vérifier si l'inscription existe déjà
            inscription_existante = InscriptionGroupe.query.filter_by(
                etudiant_id=etudiant_id, groupe_id=groupe_id
            ).first()
            
            if inscription_existante:
                return False
            
            # Vérifier la capacité du groupe
            groupe = Groupe.query.get(groupe_id)
            if groupe and groupe.nombre_etudiants >= groupe.capacite_max:
                return False
            
            inscription = InscriptionGroupe(
                etudiant_id=etudiant_id,
                groupe_id=groupe_id
            )
            
            db.session.add(inscription)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def desinscrire_etudiant_groupe(etudiant_id: int, groupe_id: int) -> bool:
        """Désinscrit un étudiant d'un groupe"""
        try:
            inscription = InscriptionGroupe.query.filter_by(
                etudiant_id=etudiant_id, groupe_id=groupe_id
            ).first()
            
            if not inscription:
                return False
            
            db.session.delete(inscription)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    # ==================== STATISTIQUES ====================
    
    @staticmethod
    def obtenir_statistiques_generales() -> dict:
        """Obtient les statistiques générales de l'institut"""
        try:
            annee_active = ServiceAcademique.obtenir_annee_active()
            if not annee_active:
                return {}
            
            stats = {
                'annee_active': annee_active.nom,
                'total_etudiants': Etudiant.query.filter_by(annee_academique_id=annee_active.id).count(),
                'total_enseignants': Enseignant.query.filter_by(statut='actif').count(),
                'total_semestres': Semestre.query.filter_by(annee_academique_id=annee_active.id).count(),
                'total_ues': 0,
                'total_matieres': 0,
                'total_groupes': 0
            }
            
            # Compter les UEs et matières
            semestres = Semestre.query.filter_by(annee_academique_id=annee_active.id).all()
            for semestre in semestres:
                ues = UniteEnseignement.query.filter_by(semestre_id=semestre.id).all()
                stats['total_ues'] += len(ues)
                
                for ue in ues:
                    matieres = Matiere.query.filter_by(unite_enseignement_id=ue.id).all()
                    stats['total_matieres'] += len(matieres)
                    
                    groupes = Groupe.query.filter_by(unite_enseignement_id=ue.id).all()
                    stats['total_groupes'] += len(groupes)
            
            return stats
        except Exception as e:
            return {} 