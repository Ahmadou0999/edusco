"""
Service pour la gestion pédagogique
Gère les notes, absences, emplois du temps et délibérations
"""

from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func
from app.extensions import db
from app.models.pedagogique import (
    Note, Absence, EmploiDuTemps, Deliberation, ResultatDeliberation
)
from app.models.academique import Etudiant, Matiere, Groupe, Enseignant, Semestre, UniteEnseignement

class ServicePedagogique:
    """Service pour la gestion pédagogique"""
    
    # ==================== GESTION DES NOTES ====================
    
    @staticmethod
    def creer_note(
        etudiant_id: int,
        matiere_id: int,
        groupe_id: int,
        enseignant_id: int,
        type_evaluation: str,
        note: float,
        coefficient: float = 1.0,
        commentaire: str = None,
        date_evaluation: date = None
    ) -> tuple[Note, bool]:
        """Crée une nouvelle note"""
        try:
            # Validation de la note
            if not (0 <= note <= 20):
                return None, False
            
            # Vérifier que l'étudiant est inscrit dans le groupe
            etudiant = Etudiant.query.get(etudiant_id)
            groupe = Groupe.query.get(groupe_id)
            
            if not etudiant or not groupe:
                return None, False
            
            # Vérifier l'inscription
            inscription = db.session.query(InscriptionGroupe).filter(
                and_(
                    InscriptionGroupe.etudiant_id == etudiant_id,
                    InscriptionGroupe.groupe_id == groupe_id
                )
            ).first()
            
            if not inscription:
                return None, False
            
            nouvelle_note = Note(
                etudiant_id=etudiant_id,
                matiere_id=matiere_id,
                groupe_id=groupe_id,
                enseignant_id=enseignant_id,
                type_evaluation=type_evaluation,
                note=note,
                coefficient=coefficient,
                commentaire=commentaire,
                date_evaluation=date_evaluation or date.today()
            )
            
            db.session.add(nouvelle_note)
            db.session.commit()
            
            return nouvelle_note, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de la note: {e}")
            return None, False
    
    @staticmethod
    def modifier_note(
        note_id: int,
        note: float = None,
        coefficient: float = None,
        commentaire: str = None,
        type_evaluation: str = None
    ) -> tuple[Note, bool]:
        """Modifie une note existante"""
        try:
            note_obj = Note.query.get(note_id)
            if not note_obj:
                return None, False
            
            if note is not None:
                if not (0 <= note <= 20):
                    return None, False
                note_obj.note = note
            
            if coefficient is not None:
                note_obj.coefficient = coefficient
            
            if commentaire is not None:
                note_obj.commentaire = commentaire
            
            if type_evaluation is not None:
                note_obj.type_evaluation = type_evaluation
            
            db.session.commit()
            return note_obj, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la modification de la note: {e}")
            return None, False
    
    @staticmethod
    def supprimer_note(note_id: int) -> bool:
        """Supprime une note"""
        try:
            note = Note.query.get(note_id)
            if not note:
                return False
            
            db.session.delete(note)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la suppression de la note: {e}")
            return False
    
    @staticmethod
    def obtenir_notes_etudiant(etudiant_id: int, matiere_id: int = None) -> List[Note]:
        """Obtient toutes les notes d'un étudiant"""
        query = Note.query.filter(Note.etudiant_id == etudiant_id)
        
        if matiere_id:
            query = query.filter(Note.matiere_id == matiere_id)
        
        return query.order_by(Note.date_evaluation.desc()).all()
    
    @staticmethod
    def calculer_moyenne_etudiant(etudiant_id: int, matiere_id: int = None) -> float:
        """Calcule la moyenne d'un étudiant"""
        query = db.session.query(
            func.avg(Note.note * Note.coefficient).label('moyenne_ponderee'),
            func.sum(Note.coefficient).label('total_coefficients')
        ).filter(Note.etudiant_id == etudiant_id)
        
        if matiere_id:
            query = query.filter(Note.matiere_id == matiere_id)
        
        result = query.first()
        
        if result and result.total_coefficients > 0:
            return result.moyenne_ponderee / result.total_coefficients
        return 0.0
    
    # ==================== GESTION DES ABSENCES ====================
    
    @staticmethod
    def creer_absence(
        etudiant_id: int,
        matiere_id: int,
        groupe_id: int,
        date_absence: date,
        heure_debut: time,
        heure_fin: time,
        motif: str = None,
        justifiee: bool = False,
        justificatif: str = None,
        commentaire: str = None
    ) -> tuple[Absence, bool]:
        """Crée une nouvelle absence"""
        try:
            nouvelle_absence = Absence(
                etudiant_id=etudiant_id,
                matiere_id=matiere_id,
                groupe_id=groupe_id,
                date_absence=date_absence,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                motif=motif,
                justifiee=justifiee,
                justificatif=justificatif,
                commentaire=commentaire
            )
            
            db.session.add(nouvelle_absence)
            db.session.commit()
            
            return nouvelle_absence, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'absence: {e}")
            return None, False
    
    @staticmethod
    def modifier_absence(
        absence_id: int,
        justifiee: bool = None,
        motif: str = None,
        justificatif: str = None,
        commentaire: str = None
    ) -> tuple[Absence, bool]:
        """Modifie une absence existante"""
        try:
            absence = Absence.query.get(absence_id)
            if not absence:
                return None, False
            
            if justifiee is not None:
                absence.justifiee = justifiee
            
            if motif is not None:
                absence.motif = motif
            
            if justificatif is not None:
                absence.justificatif = justificatif
            
            if commentaire is not None:
                absence.commentaire = commentaire
            
            db.session.commit()
            return absence, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la modification de l'absence: {e}")
            return None, False
    
    @staticmethod
    def supprimer_absence(absence_id: int) -> bool:
        """Supprime une absence"""
        try:
            absence = Absence.query.get(absence_id)
            if not absence:
                return False
            
            db.session.delete(absence)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la suppression de l'absence: {e}")
            return False
    
    @staticmethod
    def obtenir_absences_etudiant(etudiant_id: int, date_debut: date = None, date_fin: date = None) -> List[Absence]:
        """Obtient les absences d'un étudiant"""
        query = Absence.query.filter(Absence.etudiant_id == etudiant_id)
        
        if date_debut:
            query = query.filter(Absence.date_absence >= date_debut)
        
        if date_fin:
            query = query.filter(Absence.date_absence <= date_fin)
        
        return query.order_by(Absence.date_absence.desc()).all()
    
    @staticmethod
    def calculer_taux_absence_etudiant(etudiant_id: int, semestre_id: int = None) -> Dict[str, float]:
        """Calcule le taux d'absence d'un étudiant"""
        # Logique de calcul du taux d'absence
        # À implémenter selon les besoins spécifiques
        return {
            'total_heures': 0.0,
            'heures_absences': 0.0,
            'taux_absence': 0.0
        }
    
    # ==================== GESTION DES EMPLOIS DU TEMPS ====================
    
    @staticmethod
    def creer_emploi_du_temps(
        groupe_id: int,
        matiere_id: int,
        enseignant_id: int,
        semestre_id: int,
        jour: int,
        heure_debut: time,
        heure_fin: time,
        salle: str = None
    ) -> tuple[EmploiDuTemps, bool]:
        """Crée un nouvel emploi du temps"""
        try:
            # Vérifier les conflits d'emploi du temps
            conflit = EmploiDuTemps.query.filter(
                and_(
                    EmploiDuTemps.groupe_id == groupe_id,
                    EmploiDuTemps.jour == jour,
                    EmploiDuTemps.actif == True,
                    or_(
                        and_(EmploiDuTemps.heure_debut <= heure_debut, EmploiDuTemps.heure_fin > heure_debut),
                        and_(EmploiDuTemps.heure_debut < heure_fin, EmploiDuTemps.heure_fin >= heure_fin),
                        and_(EmploiDuTemps.heure_debut >= heure_debut, EmploiDuTemps.heure_fin <= heure_fin)
                    )
                )
            ).first()
            
            if conflit:
                return None, False
            
            nouvel_edt = EmploiDuTemps(
                groupe_id=groupe_id,
                matiere_id=matiere_id,
                enseignant_id=enseignant_id,
                semestre_id=semestre_id,
                jour=jour,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                salle=salle
            )
            
            db.session.add(nouvel_edt)
            db.session.commit()
            
            return nouvel_edt, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'emploi du temps: {e}")
            return None, False
    
    @staticmethod
    def obtenir_emploi_du_temps_groupe(groupe_id: int, semestre_id: int = None) -> List[EmploiDuTemps]:
        """Obtient l'emploi du temps d'un groupe"""
        query = EmploiDuTemps.query.filter(
            and_(
                EmploiDuTemps.groupe_id == groupe_id,
                EmploiDuTemps.actif == True
            )
        )
        
        if semestre_id:
            query = query.filter(EmploiDuTemps.semestre_id == semestre_id)
        
        return query.order_by(EmploiDuTemps.jour, EmploiDuTemps.heure_debut).all()
    
    @staticmethod
    def obtenir_emploi_du_temps_enseignant(enseignant_id: int, semestre_id: int = None) -> List[EmploiDuTemps]:
        """Obtient l'emploi du temps d'un enseignant"""
        query = EmploiDuTemps.query.filter(
            and_(
                EmploiDuTemps.enseignant_id == enseignant_id,
                EmploiDuTemps.actif == True
            )
        )
        
        if semestre_id:
            query = query.filter(EmploiDuTemps.semestre_id == semestre_id)
        
        return query.order_by(EmploiDuTemps.jour, EmploiDuTemps.heure_debut).all()
    
    # ==================== GESTION DES DÉLIBÉRATIONS ====================
    
    @staticmethod
    def creer_deliberation(
        semestre_id: int,
        groupe_id: int,
        commentaire: str = None
    ) -> tuple[Deliberation, bool]:
        """Crée une nouvelle délibération"""
        try:
            # Vérifier qu'il n'y a pas déjà une délibération en cours pour ce groupe/semestre
            deliberation_existante = Deliberation.query.filter(
                and_(
                    Deliberation.semestre_id == semestre_id,
                    Deliberation.groupe_id == groupe_id,
                    Deliberation.statut == Deliberation.STATUT_EN_COURS
                )
            ).first()
            
            if deliberation_existante:
                return None, False
            
            nouvelle_deliberation = Deliberation(
                semestre_id=semestre_id,
                groupe_id=groupe_id,
                commentaire=commentaire
            )
            
            db.session.add(nouvelle_deliberation)
            db.session.commit()
            
            return nouvelle_deliberation, True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de la délibération: {e}")
            return None, False
    
    @staticmethod
    def calculer_resultats_deliberation(deliberation_id: int) -> bool:
        """Calcule les résultats de délibération pour tous les étudiants du groupe"""
        try:
            deliberation = Deliberation.query.get(deliberation_id)
            if not deliberation:
                return False
            
            # Obtenir tous les étudiants du groupe
            etudiants = db.session.query(Etudiant).join(InscriptionGroupe).filter(
                InscriptionGroupe.groupe_id == deliberation.groupe_id
            ).all()
            
            for etudiant in etudiants:
                # Calculer la moyenne générale
                moyenne = ServicePedagogique.calculer_moyenne_etudiant(etudiant.id)
                
                # Calculer les crédits obtenus
                credits_obtenus = 0
                credits_totaux = 0
                
                # Logique de calcul des crédits selon les UEs validées
                # À implémenter selon les règles spécifiques
                
                # Déterminer la décision
                if moyenne >= 10.0:
                    decision = ResultatDeliberation.DECISION_ADMIS
                elif moyenne >= 8.0:
                    decision = ResultatDeliberation.DECISION_ADMIS_AVEC_RESERVE
                else:
                    decision = ResultatDeliberation.DECISION_ECHEC
                
                # Créer ou mettre à jour le résultat
                resultat = ResultatDeliberation.query.filter(
                    and_(
                        ResultatDeliberation.deliberation_id == deliberation_id,
                        ResultatDeliberation.etudiant_id == etudiant.id
                    )
                ).first()
                
                if resultat:
                    resultat.moyenne_generale = moyenne
                    resultat.credits_obtenus = credits_obtenus
                    resultat.credits_totaux = credits_totaux
                    resultat.decision = decision
                else:
                    resultat = ResultatDeliberation(
                        deliberation_id=deliberation_id,
                        etudiant_id=etudiant.id,
                        moyenne_generale=moyenne,
                        credits_obtenus=credits_obtenus,
                        credits_totaux=credits_totaux,
                        decision=decision
                    )
                    db.session.add(resultat)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du calcul des résultats: {e}")
            return False
    
    @staticmethod
    def valider_deliberation(deliberation_id: int, commentaire: str = None) -> bool:
        """Valide une délibération"""
        try:
            deliberation = Deliberation.query.get(deliberation_id)
            if not deliberation:
                return False
            
            deliberation.statut = Deliberation.STATUT_VALIDEE
            deliberation.date_validation = date.today()
            if commentaire:
                deliberation.commentaire = commentaire
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la validation de la délibération: {e}")
            return False
    
    @staticmethod
    def obtenir_deliberations_groupe(groupe_id: int) -> List[Deliberation]:
        """Obtient toutes les délibérations d'un groupe"""
        return Deliberation.query.filter(
            Deliberation.groupe_id == groupe_id
        ).order_by(Deliberation.date_deliberation.desc()).all()
    
    @staticmethod
    def obtenir_resultats_etudiant(etudiant_id: int, semestre_id: int = None) -> List[ResultatDeliberation]:
        """Obtient les résultats de délibération d'un étudiant"""
        query = db.session.query(ResultatDeliberation).join(Deliberation).filter(
            ResultatDeliberation.etudiant_id == etudiant_id
        )
        
        if semestre_id:
            query = query.filter(Deliberation.semestre_id == semestre_id)
        
        return query.order_by(Deliberation.date_deliberation.desc()).all() 