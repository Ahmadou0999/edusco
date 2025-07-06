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
from app.models.academique import Etudiant, Matiere, Groupe, Enseignant, Semestre, UniteEnseignement, InscriptionGroupe

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
        """Obtient les résultats d'un étudiant"""
        query = ResultatDeliberation.query.filter(ResultatDeliberation.etudiant_id == etudiant_id)
        
        if semestre_id:
            query = query.join(Deliberation).filter(Deliberation.semestre_id == semestre_id)
        
        return query.order_by(ResultatDeliberation.date_creation.desc()).all()
    
    # ==================== MÉTHODES POUR LES ÉTUDIANTS ====================
    
    @staticmethod
    def get_resultats_etudiant(etudiant_id: int, annee_id: int = None, semestre_id: int = None, unite_id: int = None):
        """Récupère les résultats d'un étudiant avec filtres"""
        try:
            query = Note.query.filter(Note.etudiant_id == etudiant_id)
            
            if annee_id:
                query = query.join(Matiere).join(UniteEnseignement).join(Semestre).filter(Semestre.annee_academique_id == annee_id)
            
            if semestre_id:
                query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
            
            if unite_id:
                query = query.join(Matiere).filter(Matiere.unite_enseignement_id == unite_id)
            
            return query.order_by(Note.date_evaluation.desc()).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_resultats_etudiant_publics(etudiant_id: int):
        """Récupère les résultats publics d'un étudiant (pour l'affichage public)"""
        try:
            # Pour l'instant, retourner les mêmes résultats que la méthode privée
            # Cette méthode peut être adaptée pour filtrer les informations sensibles
            return ServicePedagogique.get_resultats_etudiant(etudiant_id)
        except Exception as e:
            return []
    
    @staticmethod
    def get_emploi_du_temps_etudiant(etudiant_id: int, annee_id: int = None, semestre_id: int = None):
        """Récupère l'emploi du temps d'un étudiant"""
        try:
            # Récupérer les groupes de l'étudiant
            etudiant = Etudiant.query.get(etudiant_id)
            if not etudiant:
                return None
            
            # Récupérer les inscriptions aux groupes
            inscriptions = db.session.query(InscriptionGroupe).filter(
                InscriptionGroupe.etudiant_id == etudiant_id
            ).all()
            
            if not inscriptions:
                return None
            
            # Récupérer les emplois du temps des groupes
            groupe_ids = [inscription.groupe_id for inscription in inscriptions]
            
            query = EmploiDuTemps.query.filter(EmploiDuTemps.groupe_id.in_(groupe_ids))
            
            if annee_id:
                query = query.join(Semestre).filter(Semestre.annee_academique_id == annee_id)
            
            if semestre_id:
                query = query.filter(EmploiDuTemps.semestre_id == semestre_id)
            
            emplois = query.order_by(EmploiDuTemps.jour, EmploiDuTemps.heure_debut).all()
            
            # Organiser par horaires et jours
            emploi_organise = {}
            for emploi in emplois:
                horaire = f"{emploi.heure_debut} - {emploi.heure_fin}"
                if horaire not in emploi_organise:
                    emploi_organise[horaire] = {
                        'lundi': [], 'mardi': [], 'mercredi': [], 
                        'jeudi': [], 'vendredi': [], 'samedi': []
                    }
                
                jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
                if 0 <= emploi.jour < len(jours):
                    emploi_organise[horaire][jours[emploi.jour]].append(emploi)
            
            return emploi_organise
        except Exception as e:
            return None
    
    @staticmethod
    def get_absences_etudiant(etudiant_id: int, annee_id: int = None, semestre_id: int = None, matiere_id: int = None):
        """Récupère les absences d'un étudiant avec filtres"""
        try:
            query = Absence.query.filter(Absence.etudiant_id == etudiant_id)
            
            if annee_id:
                query = query.join(Matiere).join(UniteEnseignement).join(Semestre).filter(Semestre.annee_academique_id == annee_id)
            
            if semestre_id:
                query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
            
            if matiere_id:
                query = query.filter(Absence.matiere_id == matiere_id)
            
            return query.order_by(Absence.date_absence.desc()).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_semestres_actifs():
        """Récupère tous les semestres actifs"""
        try:
            return Semestre.query.filter_by(actif=True).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_semestres_par_annee(annee_id: int):
        """Récupère tous les semestres d'une année"""
        try:
            return Semestre.query.filter_by(annee_academique_id=annee_id).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_resultats_publics(annee_id: int = None, semestre_id: int = None, unite_id: int = None):
        """Récupère les résultats publics (pour l'affichage public)"""
        try:
            query = Note.query
            
            if annee_id:
                query = query.join(Matiere).join(UniteEnseignement).join(Semestre).filter(Semestre.annee_academique_id == annee_id)
            
            if semestre_id:
                query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
            
            if unite_id:
                query = query.join(Matiere).filter(Matiere.unite_enseignement_id == unite_id)
            
            return query.order_by(Note.date_evaluation.desc()).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_bulletin_etudiant(etudiant_id: int, annee_id: int = None, semestre_id: int = None):
        """Génère le bulletin de notes d'un étudiant"""
        try:
            from app.models.academique import Etudiant, Matiere, UniteEnseignement, Semestre, AnneeAcademique
            from app.models.pedagogique import Note
            
            etudiant = Etudiant.query.get(etudiant_id)
            if not etudiant:
                return None
            
            # Construire la requête de base
            query = Note.query.filter_by(etudiant_id=etudiant_id)
            
            # Appliquer les filtres
            if annee_id:
                query = query.join(Matiere).join(UniteEnseignement).join(Semestre).filter(Semestre.annee_academique_id == annee_id)
            
            if semestre_id:
                query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
            
            notes = query.all()
            
            # Organiser les notes par unité d'enseignement
            bulletin = {
                'etudiant': etudiant,
                'unites_enseignement': {},
                'statistiques': {
                    'total_notes': len(notes),
                    'moyenne_generale': 0.0,
                    'total_credits': 0,
                    'credits_obtenus': 0
                }
            }
            
            total_points = 0
            total_coefficients = 0
            
            for note in notes:
                unite = note.matiere.unite_enseignement
                if unite.id not in bulletin['unites_enseignement']:
                    bulletin['unites_enseignement'][unite.id] = {
                        'unite': unite,
                        'matieres': {},
                        'moyenne': 0.0,
                        'total_points': 0,
                        'total_coefficients': 0
                    }
                
                matiere = note.matiere
                if matiere.id not in bulletin['unites_enseignement'][unite.id]['matieres']:
                    bulletin['unites_enseignement'][unite.id]['matieres'][matiere.id] = {
                        'matiere': matiere,
                        'notes': [],
                        'moyenne': 0.0
                    }
                
                # Ajouter la note
                bulletin['unites_enseignement'][unite.id]['matieres'][matiere.id]['notes'].append(note)
                
                # Calculer la moyenne de la matière
                matiere_data = bulletin['unites_enseignement'][unite.id]['matieres'][matiere.id]
                matiere_data['moyenne'] = sum(n.note * n.coefficient for n in matiere_data['notes']) / sum(n.coefficient for n in matiere_data['notes'])
                
                # Ajouter aux totaux de l'unité
                unite_data = bulletin['unites_enseignement'][unite.id]
                unite_data['total_points'] += note.note * note.coefficient
                unite_data['total_coefficients'] += note.coefficient
                
                # Ajouter aux totaux généraux
                total_points += note.note * note.coefficient
                total_coefficients += note.coefficient
            
            # Calculer les moyennes des unités
            for unite_data in bulletin['unites_enseignement'].values():
                if unite_data['total_coefficients'] > 0:
                    unite_data['moyenne'] = unite_data['total_points'] / unite_data['total_coefficients']
            
            # Calculer la moyenne générale
            if total_coefficients > 0:
                bulletin['statistiques']['moyenne_generale'] = total_points / total_coefficients
            
            # Calculer les crédits
            for unite_data in bulletin['unites_enseignement'].values():
                unite = unite_data['unite']
                bulletin['statistiques']['total_credits'] += unite.credits
                
                # Un étudiant obtient les crédits si sa moyenne est >= 10
                if unite_data['moyenne'] >= 10:
                    bulletin['statistiques']['credits_obtenus'] += unite.credits
            
            return bulletin
            
        except Exception as e:
            print(f"Erreur lors de la génération du bulletin: {e}")
            return None

    @staticmethod
    def get_resultats_etudiant(etudiant_id: int):
        """Récupère les résultats complets d'un étudiant"""
        try:
            from app.models.academique import Etudiant
            from app.models.pedagogique import Note, Absence
            
            etudiant = Etudiant.query.get(etudiant_id)
            if not etudiant:
                return None
            
            # Récupérer les notes récentes
            notes_recentes = Note.query.filter_by(etudiant_id=etudiant_id)\
                .order_by(Note.date_evaluation.desc())\
                .limit(10)\
                .all()
            
            # Calculer les statistiques
            toutes_notes = Note.query.filter_by(etudiant_id=etudiant_id).all()
            total_notes = len(toutes_notes)
            
            if total_notes > 0:
                moyenne_generale = sum(note.note * note.coefficient for note in toutes_notes) / sum(note.coefficient for note in toutes_notes)
            else:
                moyenne_generale = 0.0
            
            # Compter les absences
            total_absences = Absence.query.filter_by(etudiant_id=etudiant_id).count()
            
            # Calculer les crédits obtenus (simplifié)
            credits_obtenus = 0
            if moyenne_generale >= 10:
                # Logique simplifiée pour les crédits
                credits_obtenus = int(moyenne_generale * 2)  # Exemple
            
            return {
                'total_notes': total_notes,
                'moyenne_generale': moyenne_generale,
                'total_absences': total_absences,
                'credits_obtenus': credits_obtenus,
                'notes_recentes': notes_recentes
            }
            
        except Exception as e:
            print(f"Erreur lors de la récupération des résultats: {e}")
            return None
    
    # ==================== MÉTHODES POUR LES ENSEIGNANTS ====================
    
    @staticmethod
    def compter_notes_par_enseignant(enseignant_id: int) -> int:
        """Compte le nombre de notes saisies par un enseignant"""
        try:
            return Note.query.filter_by(enseignant_id=enseignant_id).count()
        except Exception as e:
            return 0
    
    @staticmethod
    def compter_absences_par_enseignant(enseignant_id: int) -> int:
        """Compte le nombre d'absences saisies par un enseignant"""
        try:
            return Absence.query.filter_by(enseignant_id=enseignant_id).count()
        except Exception as e:
            return 0
    
    @staticmethod
    def get_activites_recentes_enseignant(enseignant_id: int, limit: int = 10):
        """Récupère les activités récentes d'un enseignant"""
        try:
            # Combiner notes et absences récentes
            notes = Note.query.filter_by(enseignant_id=enseignant_id).order_by(Note.date_evaluation.desc()).limit(limit//2).all()
            absences = Absence.query.filter_by(enseignant_id=enseignant_id).order_by(Absence.date_absence.desc()).limit(limit//2).all()
            
            activites = []
            for note in notes:
                activites.append({
                    'type': 'note',
                    'date_creation': note.date_evaluation,
                    'titre': f'Note saisie',
                    'description': f'Note {note.note}/20 pour {note.etudiant.nom_complet} en {note.matiere.nom}',
                    'objet': note
                })
            
            for absence in absences:
                activites.append({
                    'type': 'absence',
                    'date_creation': absence.date_absence,
                    'titre': f'Absence enregistrée',
                    'description': f'Absence de {absence.etudiant.nom_complet} en {absence.matiere.nom}',
                    'objet': absence
                })
            
            # Trier par date
            activites.sort(key=lambda x: x['date_creation'], reverse=True)
            return activites[:limit]
        except Exception as e:
            return []
    
    @staticmethod
    def get_notes_par_enseignant(enseignant_id: int, matiere_id: int = None, groupe_id: int = None, semestre_id: int = None):
        """Récupère les notes d'un enseignant avec filtres"""
        try:
            query = Note.query.filter_by(enseignant_id=enseignant_id)
            
            if matiere_id:
                query = query.filter_by(matiere_id=matiere_id)
            
            if groupe_id:
                query = query.filter_by(groupe_id=groupe_id)
            
            if semestre_id:
                query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
            
            return query.order_by(Note.date_evaluation.desc()).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_notes_par_enseignant_paginees(enseignant_id: int, page: int = 1, per_page: int = 25, matiere_id: int = None, groupe_id: int = None, semestre_id: int = None):
        """
        Récupère les notes d'un enseignant avec pagination
        
        Args:
            enseignant_id: ID de l'enseignant
            page: Numéro de page
            per_page: Nombre d'éléments par page
            matiere_id: ID de la matière (filtre optionnel)
            groupe_id: ID du groupe (filtre optionnel)
            semestre_id: ID du semestre (filtre optionnel)
            
        Returns:
            Pagination object: Objet paginé des notes
        """
        query = Note.query.filter_by(enseignant_id=enseignant_id)
        
        if matiere_id:
            query = query.filter_by(matiere_id=matiere_id)
        
        if groupe_id:
            query = query.filter_by(groupe_id=groupe_id)
        
        if semestre_id:
            query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
        
        return query.order_by(Note.date_saisie.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def get_note_par_id(note_id: int):
        """Récupère une note par son ID"""
        try:
            return Note.query.get(note_id)
        except Exception as e:
            return None
    
    @staticmethod
    def sauvegarder_notes(enseignant_id: int, matiere_id: int, groupe_id: int, semestre_id: int, notes_data: list):
        """Sauvegarde les notes pour un groupe"""
        try:
            # Récupérer la matière pour obtenir son coefficient
            matiere = Matiere.query.get(matiere_id)
            if not matiere:
                raise ValueError("Matière non trouvée")
            
            coefficient_matiere = matiere.coefficient
            
            for note_data in notes_data:
                etudiant_id = note_data.get('etudiant_id')
                note_value = note_data.get('note')
                type_evaluation = note_data.get('type_evaluation', 'Contrôle')
                date_evaluation = note_data.get('date_evaluation', date.today())
                commentaire = note_data.get('commentaire', '')
                
                if etudiant_id and note_value is not None:
                    # Vérifier si la note existe déjà
                    note_existante = Note.query.filter_by(
                        etudiant_id=etudiant_id,
                        matiere_id=matiere_id,
                        groupe_id=groupe_id,
                        enseignant_id=enseignant_id,
                        type_evaluation=type_evaluation
                    ).first()
                    
                    if note_existante:
                        # Modifier la note existante
                        note_existante.note = float(note_value)
                        note_existante.coefficient = coefficient_matiere  # Utiliser le coefficient de la matière
                        note_existante.commentaire = commentaire
                        note_existante.date_evaluation = date_evaluation
                    else:
                        # Créer une nouvelle note
                        nouvelle_note = Note(
                            etudiant_id=etudiant_id,
                            matiere_id=matiere_id,
                            groupe_id=groupe_id,
                            enseignant_id=enseignant_id,
                            note=float(note_value),
                            coefficient=coefficient_matiere,  # Utiliser le coefficient de la matière
                            type_evaluation=type_evaluation,
                            commentaire=commentaire,
                            date_evaluation=date_evaluation
                        )
                        db.session.add(nouvelle_note)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def valider_notes(enseignant_id: int, matiere_id: int, groupe_id: int, semestre_id: int, notes_data: list, type_evaluation: str, date_evaluation: str, commentaire: str):
        """
        Valider les notes (les rendre définitives)
        
        Args:
            enseignant_id: ID de l'enseignant
            matiere_id: ID de la matière
            groupe_id: ID du groupe
            semestre_id: ID du semestre
            notes_data: Liste des notes à valider
            type_evaluation: Type d'évaluation
            date_evaluation: Date d'évaluation
            commentaire: Commentaire général
            
        Returns:
            bool: True si la validation a réussi
        """
        try:
            # Récupérer le coefficient de la matière
            matiere = Matiere.query.get(matiere_id)
            coefficient_matiere = matiere.coefficient if matiere else 1.0
            
            # Convertir la date d'évaluation
            date_evaluation = datetime.strptime(date_evaluation, '%Y-%m-%d').date()
            
            for note_data in notes_data:
                etudiant_id = note_data.get('etudiant_id')
                note_value = note_data.get('note')
                appreciation = note_data.get('appreciation', '')
                
                if etudiant_id and note_value is not None:
                    # Vérifier si la note existe déjà
                    note_existante = Note.query.filter_by(
                        etudiant_id=etudiant_id,
                        matiere_id=matiere_id,
                        groupe_id=groupe_id,
                        enseignant_id=enseignant_id,
                        type_evaluation=type_evaluation
                    ).first()
                    
                    if note_existante:
                        # Modifier la note existante et la valider
                        note_existante.note = float(note_value)
                        note_existante.coefficient = coefficient_matiere
                        note_existante.commentaire = commentaire
                        note_existante.date_evaluation = date_evaluation
                        note_existante.validee = True
                        note_existante.validee_par = enseignant_id
                        note_existante.date_validation = datetime.utcnow()
                        note_existante.commentaire_validation = f"Validé par l'enseignant - {appreciation}"
                    else:
                        # Créer une nouvelle note validée
                        nouvelle_note = Note(
                            etudiant_id=etudiant_id,
                            matiere_id=matiere_id,
                            groupe_id=groupe_id,
                            enseignant_id=enseignant_id,
                            note=float(note_value),
                            coefficient=coefficient_matiere,
                            type_evaluation=type_evaluation,
                            commentaire=commentaire,
                            date_evaluation=date_evaluation,
                            validee=True,
                            validee_par=enseignant_id,
                            date_validation=datetime.utcnow(),
                            commentaire_validation=f"Validé par l'enseignant - {appreciation}"
                        )
                        db.session.add(nouvelle_note)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def sauvegarder_absences(enseignant_id: int, matiere_id: int, groupe_id: int, date_absence: str, absences_data: list, heure_debut: str = None, heure_fin: str = None, motif: str = None):
        """
        Sauvegarde les absences saisies par un enseignant
        
        Args:
            enseignant_id: ID de l'enseignant
            matiere_id: ID de la matière
            groupe_id: ID du groupe
            date_absence: Date d'absence (format YYYY-MM-DD)
            absences_data: Liste des absences à sauvegarder
            heure_debut: Heure de début (format HH:MM)
            heure_fin: Heure de fin (format HH:MM)
            motif: Motif général des absences
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        try:
            # Convertir la date d'absence
            date_absence = datetime.strptime(date_absence, '%Y-%m-%d').date()
            
            # Convertir les heures si fournies
            heure_debut_time = None
            heure_fin_time = None
            
            if heure_debut:
                heure_debut_time = datetime.strptime(heure_debut, '%H:%M').time()
            if heure_fin:
                heure_fin_time = datetime.strptime(heure_fin, '%H:%M').time()
            
            for absence_data in absences_data:
                etudiant_id = absence_data.get('etudiant_id')
                justifiee = absence_data.get('justifiee', False)
                
                if etudiant_id:
                    # Vérifier si l'absence existe déjà
                    absence_existante = Absence.query.filter_by(
                        etudiant_id=etudiant_id,
                        matiere_id=matiere_id,
                        groupe_id=groupe_id,
                        enseignant_id=enseignant_id,
                        date_absence=date_absence
                    ).first()
                    
                    if absence_existante:
                        # Modifier l'absence existante
                        absence_existante.justifiee = justifiee
                        if motif:
                            absence_existante.motif = motif
                        if heure_debut_time:
                            absence_existante.heure_debut = heure_debut_time
                        if heure_fin_time:
                            absence_existante.heure_fin = heure_fin_time
                    else:
                        # Créer une nouvelle absence
                        nouvelle_absence = Absence(
                            etudiant_id=etudiant_id,
                            matiere_id=matiere_id,
                            groupe_id=groupe_id,
                            enseignant_id=enseignant_id,
                            date_absence=date_absence,
                            heure_debut=heure_debut_time or time(8, 0),  # Heure par défaut
                            heure_fin=heure_fin_time or time(10, 0),    # Heure par défaut
                            motif=motif,
                            justifiee=justifiee
                        )
                        db.session.add(nouvelle_absence)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def generer_rapport_notes_enseignant(enseignant_id: int, matiere_id: int = None, groupe_id: int = None, semestre_id: int = None):
        """Génère un rapport des notes pour un enseignant"""
        try:
            notes = ServicePedagogique.get_notes_par_enseignant(enseignant_id, matiere_id, groupe_id, semestre_id)
            
            if not notes:
                return {
                    'total_notes': 0,
                    'moyenne_generale': 0,
                    'notes_par_matiere': {},
                    'notes_par_groupe': {},
                    'distribution': {'0-5': 0, '5-10': 0, '10-15': 0, '15-20': 0}
                }
            
            # Calculs statistiques
            total_notes = len(notes)
            moyenne_generale = sum(note.note for note in notes) / total_notes
            
            # Distribution des notes
            distribution = {'0-5': 0, '5-10': 0, '10-15': 0, '15-20': 0}
            for note in notes:
                if note.note < 5:
                    distribution['0-5'] += 1
                elif note.note < 10:
                    distribution['5-10'] += 1
                elif note.note < 15:
                    distribution['10-15'] += 1
                else:
                    distribution['15-20'] += 1
            
            # Notes par matière
            notes_par_matiere = {}
            for note in notes:
                matiere_nom = note.matiere.nom
                if matiere_nom not in notes_par_matiere:
                    notes_par_matiere[matiere_nom] = []
                notes_par_matiere[matiere_nom].append(note.note)
            
            # Notes par groupe
            notes_par_groupe = {}
            for note in notes:
                groupe_nom = note.groupe.nom
                if groupe_nom not in notes_par_groupe:
                    notes_par_groupe[groupe_nom] = []
                notes_par_groupe[groupe_nom].append(note.note)
            
            return {
                'total_notes': total_notes,
                'moyenne_generale': moyenne_generale,
                'notes_par_matiere': notes_par_matiere,
                'notes_par_groupe': notes_par_groupe,
                'distribution': distribution
            }
        except Exception as e:
            return {
                'total_notes': 0,
                'moyenne_generale': 0,
                'notes_par_matiere': {},
                'notes_par_groupe': {},
                'distribution': {'0-5': 0, '5-10': 0, '10-15': 0, '15-20': 0}
            }

    @staticmethod
    def get_absences_par_enseignant(enseignant_id: int, matiere_id: int = None, groupe_id: int = None, date_debut: str = None, date_fin: str = None):
        """Récupère les absences saisies par un enseignant"""
        try:
            query = Absence.query.filter(Absence.enseignant_id == enseignant_id)
            
            if matiere_id:
                query = query.filter(Absence.matiere_id == matiere_id)
            
            if groupe_id:
                query = query.filter(Absence.groupe_id == groupe_id)
            
            if date_debut:
                query = query.filter(Absence.date_absence >= date_debut)
            
            if date_fin:
                query = query.filter(Absence.date_absence <= date_fin)
            
            return query.order_by(Absence.date_absence.desc()).all()
            
        except Exception as e:
            print(f"Erreur lors de la récupération des absences: {e}")
            return []

    @staticmethod
    def get_absences_par_enseignant_paginees(enseignant_id: int, page: int = 1, per_page: int = 25, matiere_id: int = None, groupe_id: int = None, date_debut: str = None, date_fin: str = None):
        """
        Récupère les absences d'un enseignant avec pagination
        
        Args:
            enseignant_id: ID de l'enseignant
            page: Numéro de page
            per_page: Nombre d'éléments par page
            matiere_id: ID de la matière (filtre optionnel)
            groupe_id: ID du groupe (filtre optionnel)
            date_debut: Date de début (filtre optionnel)
            date_fin: Date de fin (filtre optionnel)
            
        Returns:
            Pagination object: Objet paginé des absences
        """
        query = Absence.query.filter_by(enseignant_id=enseignant_id)
        
        if matiere_id:
            query = query.filter_by(matiere_id=matiere_id)
        
        if groupe_id:
            query = query.filter_by(groupe_id=groupe_id)
        
        if date_debut:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            query = query.filter(Absence.date_absence >= date_debut_obj)
        
        if date_fin:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            query = query.filter(Absence.date_absence <= date_fin_obj)
        
        return query.order_by(Absence.date_absence.desc(), Absence.heure_debut.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

    @staticmethod
    def generer_rapport_absences_enseignant(enseignant_id: int, matiere_id: int = None, groupe_id: int = None, date_debut: str = None, date_fin: str = None):
        """Génère un rapport des absences pour un enseignant"""
        try:
            absences = ServicePedagogique.get_absences_par_enseignant(
                enseignant_id, matiere_id, groupe_id, date_debut, date_fin
            )
            
            if not absences:
                return {
                    'total_absences': 0,
                    'absences_justifiees': 0,
                    'absences_non_justifiees': 0,
                    'taux_justification': 0,
                    'absences_par_matiere': {},
                    'absences_par_groupe': {},
                    'absences_par_date': {}
                }
            
            # Calculs statistiques
            total_absences = len(absences)
            absences_justifiees = len([a for a in absences if a.justifiee])
            absences_non_justifiees = total_absences - absences_justifiees
            taux_justification = (absences_justifiees / total_absences * 100) if total_absences > 0 else 0
            
            # Absences par matière
            absences_par_matiere = {}
            for absence in absences:
                matiere_nom = absence.matiere.nom if absence.matiere else 'Matière inconnue'
                if matiere_nom not in absences_par_matiere:
                    absences_par_matiere[matiere_nom] = {'total': 0, 'justifiees': 0, 'non_justifiees': 0}
                absences_par_matiere[matiere_nom]['total'] += 1
                if absence.justifiee:
                    absences_par_matiere[matiere_nom]['justifiees'] += 1
                else:
                    absences_par_matiere[matiere_nom]['non_justifiees'] += 1
            
            # Absences par groupe
            absences_par_groupe = {}
            for absence in absences:
                groupe_nom = absence.groupe.nom if absence.groupe else 'Groupe inconnu'
                if groupe_nom not in absences_par_groupe:
                    absences_par_groupe[groupe_nom] = {'total': 0, 'justifiees': 0, 'non_justifiees': 0}
                absences_par_groupe[groupe_nom]['total'] += 1
                if absence.justifiee:
                    absences_par_groupe[groupe_nom]['justifiees'] += 1
                else:
                    absences_par_groupe[groupe_nom]['non_justifiees'] += 1
            
            # Absences par date
            absences_par_date = {}
            for absence in absences:
                date_str = absence.date_absence.strftime('%Y-%m-%d')
                if date_str not in absences_par_date:
                    absences_par_date[date_str] = {'total': 0, 'justifiees': 0, 'non_justifiees': 0}
                absences_par_date[date_str]['total'] += 1
                if absence.justifiee:
                    absences_par_date[date_str]['justifiees'] += 1
                else:
                    absences_par_date[date_str]['non_justifiees'] += 1
            
            return {
                'total_absences': total_absences,
                'absences_justifiees': absences_justifiees,
                'absences_non_justifiees': absences_non_justifiees,
                'taux_justification': round(taux_justification, 2),
                'absences_par_matiere': absences_par_matiere,
                'absences_par_groupe': absences_par_groupe,
                'absences_par_date': absences_par_date
            }
        except Exception as e:
            return {
                'total_absences': 0,
                'absences_justifiees': 0,
                'absences_non_justifiees': 0,
                'taux_justification': 0,
                'absences_par_matiere': {},
                'absences_par_groupe': {},
                'absences_par_date': {}
            } 