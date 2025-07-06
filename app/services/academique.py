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
    def modifier_semestre(semestre_id: int, nom: str, code: str, date_debut: date, 
                         date_fin: date, annee_id: int, actif: bool) -> bool:
        """Modifie un semestre existant"""
        try:
            semestre = Semestre.query.get(semestre_id)
            if not semestre:
                return False
            
            # Vérifier si le code existe déjà pour un autre semestre
            if code != semestre.code:
                code_existant = Semestre.query.filter(
                    Semestre.code == code,
                    Semestre.id != semestre_id
                ).first()
                if code_existant:
                    return False
            
            # Mettre à jour les informations
            semestre.nom = nom
            semestre.code = code
            semestre.date_debut = date_debut
            semestre.date_fin = date_fin
            semestre.annee_academique_id = annee_id
            semestre.actif = actif
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def obtenir_semestres_par_annee(annee_id: int) -> List[Semestre]:
        """Obtient tous les semestres d'une année académique"""
        return Semestre.query.filter_by(annee_academique_id=annee_id).order_by(Semestre.code).all()
    
    @staticmethod
    def obtenir_tous_semestres() -> List[Semestre]:
        """Obtient tous les semestres"""
        return Semestre.query.order_by(Semestre.annee_academique_id, Semestre.code).all()
    
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
    def modifier_unite_enseignement(ue_id: int, code: str, nom: str, description: str,
                                   credits: int, coefficient: float, semestre_id: int) -> bool:
        """Modifie une unité d'enseignement existante"""
        try:
            ue = UniteEnseignement.query.get(ue_id)
            if not ue:
                return False
            
            # Vérifier si le code existe déjà pour une autre UE
            if code != ue.code:
                code_existant = UniteEnseignement.query.filter(
                    UniteEnseignement.code == code,
                    UniteEnseignement.id != ue_id
                ).first()
                if code_existant:
                    return False
            
            # Mettre à jour les informations
            ue.code = code
            ue.nom = nom
            ue.description = description
            ue.credits = credits
            ue.coefficient = coefficient
            ue.semestre_id = semestre_id
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def obtenir_ues_par_semestre(semestre_id: int) -> List[UniteEnseignement]:
        """Obtient toutes les UEs d'un semestre"""
        return UniteEnseignement.query.filter_by(semestre_id=semestre_id).order_by(UniteEnseignement.code).all()
    
    @staticmethod
    def obtenir_toutes_unites_enseignement() -> List[UniteEnseignement]:
        """Obtient toutes les unités d'enseignement"""
        return UniteEnseignement.query.order_by(UniteEnseignement.code).all()
    
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
    def obtenir_toutes_matieres() -> List[Matiere]:
        """Obtient toutes les matières"""
        return Matiere.query.order_by(Matiere.code).all()
    
    @staticmethod
    def obtenir_matieres_par_enseignant(enseignant_id: int) -> List[Matiere]:
        """Obtient toutes les matières d'un enseignant"""
        return Matiere.query.filter_by(enseignant_id=enseignant_id).order_by(Matiere.code).all()
    
    @staticmethod
    def get_matiere_par_id(matiere_id: int) -> Optional[Matiere]:
        """Récupère une matière par son ID"""
        try:
            return Matiere.query.get(matiere_id)
        except Exception as e:
            return None
    
    # ==================== ÉTUDIANTS ====================
    
    @staticmethod
    def creer_etudiant(matricule: str, nom: str, prenom: str, date_naissance: date, sexe: str, 
                      lieu_naissance: str = None, adresse: str = None, telephone: str = None, 
                      email: str = None, annee_id: int = None) -> Tuple[Etudiant, bool]:
        """Crée un nouvel étudiant et son compte utilisateur"""
        from app.services.authentification import ServiceAuthentification
        
        try:
            # Si aucune année n'est spécifiée, utiliser l'année active
            if not annee_id:
                annee_active = ServiceAcademique.obtenir_annee_active()
                if not annee_active:
                    return None, False
                annee_id = annee_active.id
            
            # Créer l'étudiant
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
            db.session.flush()  # Pour obtenir l'ID de l'étudiant
            
            # Créer le compte utilisateur pour l'étudiant
            if email:
                # Utiliser l'email fourni
                email_utilisateur = email
            else:
                # Créer un email basé sur le matricule
                email_utilisateur = f"{matricule.lower()}@edusco.com"
            
            # Mot de passe par défaut : matricule + année de naissance
            mot_de_passe_defaut = f"{matricule}{date_naissance.year}"
            
            # Créer l'utilisateur
            utilisateur, succes_utilisateur = ServiceAuthentification.creer_utilisateur(
                nom=nom,
                prenom=prenom,
                email=email_utilisateur,
                mot_de_passe=mot_de_passe_defaut,
                role='etudiant'
            )
            
            if succes_utilisateur and utilisateur:
                # Lier l'étudiant à l'utilisateur
                etudiant.utilisateur_id = utilisateur.id
                db.session.commit()
                return etudiant, True
            else:
                # Si la création de l'utilisateur échoue, supprimer l'étudiant
                db.session.rollback()
                return None, False
                
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de l'étudiant: {e}")
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
    def obtenir_tous_etudiants() -> List[Etudiant]:
        """Obtient tous les étudiants"""
        return Etudiant.query.order_by(Etudiant.nom, Etudiant.prenom).all()
    
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
    
    @staticmethod
    def modifier_enseignant(enseignant_id: int, matricule: str, nom: str, prenom: str, 
                           date_naissance: date, sexe: str, date_embauche: date,
                           lieu_naissance: str = None, adresse: str = None,
                           telephone: str = None, email: str = None, 
                           specialite: str = None, grade: str = None,
                           statut: str = 'actif') -> Tuple[Enseignant, bool]:
        """Modifie un enseignant existant"""
        try:
            enseignant = Enseignant.query.get(enseignant_id)
            if not enseignant:
                return None, False
            
            # Vérifier si le matricule existe déjà pour un autre enseignant
            if matricule != enseignant.matricule:
                matricule_existant = Enseignant.query.filter(
                    Enseignant.matricule == matricule,
                    Enseignant.id != enseignant_id
                ).first()
                if matricule_existant:
                    return None, False
            
            # Vérifier si l'email existe déjà pour un autre enseignant (si email fourni)
            if email and email != enseignant.email:
                email_existant = Enseignant.query.filter(
                    Enseignant.email == email,
                    Enseignant.id != enseignant_id
                ).first()
                if email_existant:
                    return None, False
            
            # Mettre à jour les informations
            enseignant.matricule = matricule
            enseignant.nom = nom
            enseignant.prenom = prenom
            enseignant.date_naissance = date_naissance
            enseignant.sexe = sexe
            enseignant.date_embauche = date_embauche
            enseignant.lieu_naissance = lieu_naissance
            enseignant.adresse = adresse
            enseignant.telephone = telephone
            enseignant.email = email
            enseignant.specialite = specialite
            enseignant.grade = grade
            enseignant.statut = statut
            
            db.session.commit()
            return enseignant, True
            
        except Exception as e:
            db.session.rollback()
            return None, False
    
    @staticmethod
    def changer_statut_enseignant(enseignant_id: int, nouveau_statut: str) -> Tuple[Enseignant, bool]:
        """Change le statut d'un enseignant"""
        try:
            enseignant = Enseignant.query.get(enseignant_id)
            if not enseignant:
                return None, False
            
            # Valider le statut
            statuts_valides = ['actif', 'inactif', 'retraite', 'demissionne']
            if nouveau_statut not in statuts_valides:
                return None, False
            
            enseignant.statut = nouveau_statut
            db.session.commit()
            return enseignant, True
            
        except Exception as e:
            db.session.rollback()
            return None, False
    
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
    def obtenir_tous_groupes() -> List[Groupe]:
        """Obtient tous les groupes"""
        return Groupe.query.order_by(Groupe.code).all()
    
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
            total_etudiants = Etudiant.query.count()
            total_enseignants = Enseignant.query.count()
            total_matieres = Matiere.query.count()
            total_groupes = Groupe.query.count()
            
            annee_active = ServiceAcademique.obtenir_annee_active()
            etudiants_annee_active = 0
            if annee_active:
                etudiants_annee_active = Etudiant.query.filter_by(annee_academique_id=annee_active.id).count()
            
            # Données pour les graphiques (exemples)
            labels_inscriptions = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
            data_inscriptions = [12, 19, 15, 25, 22, 30]
            
            labels_filieres = ['Informatique', 'Gestion', 'Marketing', 'Finance']
            data_filieres = [30, 25, 20, 25]
            couleurs_filieres = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e']
            
            # Données pour les filières (exemples)
            filieres = [
                {'nom': 'Informatique', 'couleur': 'primary'},
                {'nom': 'Gestion', 'couleur': 'success'},
                {'nom': 'Marketing', 'couleur': 'info'},
                {'nom': 'Finance', 'couleur': 'warning'}
            ]
            
            return {
                'total_etudiants': total_etudiants,
                'total_enseignants': total_enseignants,
                'total_matieres': total_matieres,
                'total_groupes': total_groupes,
                'etudiants_annee_active': etudiants_annee_active,
                'annee_active': annee_active.nom if annee_active else None,
                # Données pour les graphiques
                'labels_inscriptions': labels_inscriptions,
                'data_inscriptions': data_inscriptions,
                'labels_filieres': labels_filieres,
                'data_filieres': data_filieres,
                'couleurs_filieres': couleurs_filieres,
                'filieres': filieres,
                # Données pour les cartes
                'etudiants': total_etudiants,
                'enseignants': total_enseignants,
                'groupes': total_groupes,
                'matieres': total_matieres
            }
        except Exception as e:
            return {
                'total_etudiants': 0,
                'total_enseignants': 0,
                'total_matieres': 0,
                'total_groupes': 0,
                'etudiants_annee_active': 0,
                'annee_active': None,
                # Données par défaut pour les graphiques
                'labels_inscriptions': [],
                'data_inscriptions': [],
                'labels_filieres': [],
                'data_filieres': [],
                'couleurs_filieres': [],
                'filieres': [],
                # Données par défaut pour les cartes
                'etudiants': 0,
                'enseignants': 0,
                'groupes': 0,
                'matieres': 0
            }
    
    # ==================== MÉTHODES POUR LES ÉTUDIANTS ====================
    
    @staticmethod
    def get_etudiant_par_utilisateur(utilisateur_id: int):
        """Récupère un étudiant par l'ID de l'utilisateur connecté"""
        try:
            # Pour l'instant, on suppose que l'email de l'utilisateur correspond à l'email de l'étudiant
            # Cette logique peut être adaptée selon vos besoins
            from app.models.utilisateur import Utilisateur
            utilisateur = Utilisateur.query.get(utilisateur_id)
            if not utilisateur:
                return None
            
            # Chercher l'étudiant par email
            etudiant = Etudiant.query.filter_by(email=utilisateur.email).first()
            return etudiant
        except Exception as e:
            return None
    
    @staticmethod
    def get_etudiant_par_id(etudiant_id: int):
        """Récupère un étudiant par son ID"""
        try:
            return Etudiant.query.get(etudiant_id)
        except Exception as e:
            return None
    
    @staticmethod
    def get_enseignant_par_id(enseignant_id: int):
        """Récupère un enseignant par son ID"""
        try:
            return Enseignant.query.get(enseignant_id)
        except Exception as e:
            return None
    
    @staticmethod
    def get_annees_academiques():
        """Récupère toutes les années académiques"""
        try:
            return AnneeAcademique.query.order_by(AnneeAcademique.nom.desc()).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_unites_enseignement_actives():
        """Récupère toutes les unités d'enseignement actives"""
        try:
            return UniteEnseignement.query.all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_matieres_actives():
        """Récupère toutes les matières actives"""
        try:
            return Matiere.query.all()
        except Exception as e:
            return []
    
    @staticmethod
    def rechercher_enseignants(terme: str):
        """Recherche des enseignants par nom ou prénom"""
        try:
            return Enseignant.query.filter(
                db.or_(
                    Enseignant.nom.ilike(f'%{terme}%'),
                    Enseignant.prenom.ilike(f'%{terme}%'),
                    Enseignant.matricule.ilike(f'%{terme}%')
                )
            ).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_informations_academiques_etudiant(etudiant_id: int):
        """Récupère les informations académiques d'un étudiant"""
        try:
            etudiant = Etudiant.query.get(etudiant_id)
            if not etudiant:
                return None
            
            # Récupérer l'année académique active
            annee_active = ServiceAcademique.obtenir_annee_active()
            
            # Récupérer le semestre actif
            semestre_actif = None
            if annee_active:
                semestre_actif = Semestre.query.filter_by(annee_academique_id=annee_active.id, actif=True).first()
            
            return {
                'etudiant': etudiant,
                'annee_academique': annee_active,
                'semestre_actuel': semestre_actif,
                'niveau': 'Niveau à définir',  # À adapter selon votre logique
                'specialite': 'Spécialité à définir'  # À adapter selon votre logique
            }
        except Exception as e:
            return None
    
    # ==================== MÉTHODES DE COMPTAGE ET STATISTIQUES ====================
    
    @staticmethod
    def compter_etudiants(annee_id: int = None) -> int:
        """Compte le nombre total d'étudiants"""
        try:
            query = Etudiant.query
            if annee_id:
                query = query.filter_by(annee_academique_id=annee_id)
            return query.count()
        except Exception as e:
            return 0
    
    @staticmethod
    def compter_enseignants() -> int:
        """Compte le nombre total d'enseignants"""
        try:
            return Enseignant.query.count()
        except Exception as e:
            return 0
    
    @staticmethod
    def compter_matieres() -> int:
        """Compte le nombre total de matières"""
        try:
            return Matiere.query.count()
        except Exception as e:
            return 0
    
    @staticmethod
    def get_annee_academique_actuelle():
        """Récupère l'année académique actuelle"""
        try:
            return ServiceAcademique.obtenir_annee_active()
        except Exception as e:
            return None
    
    @staticmethod
    def get_enseignants_actifs():
        """Récupère tous les enseignants actifs"""
        try:
            return Enseignant.query.filter_by(statut='actif').all()
        except Exception as e:
            return []
    
    # ==================== MÉTHODES POUR LES ENSEIGNANTS ====================
    
    @staticmethod
    def enseignant_enseigne_matiere_groupe(enseignant_id: int, matiere_id: int, groupe_id: int) -> bool:
        """Vérifie si un enseignant enseigne une matière dans un groupe"""
        try:
            # Vérifier que l'enseignant enseigne cette matière
            matiere = Matiere.query.filter_by(id=matiere_id, enseignant_id=enseignant_id).first()
            if not matiere:
                return False
            
            # Vérifier que le groupe appartient à la même UE que la matière
            groupe = Groupe.query.get(groupe_id)
            if not groupe or groupe.unite_enseignement_id != matiere.unite_enseignement_id:
                return False
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def get_etudiants_par_groupe(groupe_id: int):
        """Récupère tous les étudiants d'un groupe"""
        try:
            return db.session.query(Etudiant).join(InscriptionGroupe).filter(
                InscriptionGroupe.groupe_id == groupe_id
            ).order_by(Etudiant.nom, Etudiant.prenom).all()
        except Exception as e:
            return []
    
    @staticmethod
    def get_groupe_par_id(groupe_id: int) -> Optional[Groupe]:
        """Récupère un groupe par son ID"""
        try:
            return Groupe.query.get(groupe_id)
        except Exception as e:
            return None 

# ==================== SERVICES POUR GROUPES GÉNÉRIQUES ====================

    @staticmethod
    def creer_groupe_generique(nom: str, code: str, capacite_max: int, 
                              enseignant_id: int = None, description: str = None) -> Tuple['GroupeGenerique', bool]:
        """Crée un nouveau groupe générique"""
        try:
            from app.models.academique import GroupeGenerique
            
            groupe = GroupeGenerique(
                nom=nom,
                code=code,
                capacite_max=capacite_max,
                enseignant_responsable_id=enseignant_id,
                description=description
            )
            
            db.session.add(groupe)
            db.session.commit()
            return groupe, True
        except Exception as e:
            db.session.rollback()
            return None, False

    @staticmethod
    def modifier_groupe_generique(groupe_id: int, nom: str, code: str, capacite_max: int,
                                 enseignant_id: int = None, description: str = None) -> bool:
        """Modifie un groupe générique existant"""
        try:
            from app.models.academique import GroupeGenerique
            
            groupe = GroupeGenerique.query.get(groupe_id)
            if not groupe:
                return False
            
            # Vérifier si le code existe déjà pour un autre groupe
            if code != groupe.code:
                code_existant = GroupeGenerique.query.filter(
                    GroupeGenerique.code == code,
                    GroupeGenerique.id != groupe_id
                ).first()
                if code_existant:
                    return False
            
            # Mettre à jour les informations
            groupe.nom = nom
            groupe.code = code
            groupe.capacite_max = capacite_max
            groupe.enseignant_responsable_id = enseignant_id
            groupe.description = description
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def obtenir_tous_groupes_generiques() -> List['GroupeGenerique']:
        """Obtient tous les groupes génériques"""
        try:
            from app.models.academique import GroupeGenerique
            return GroupeGenerique.query.order_by(GroupeGenerique.code).all()
        except Exception as e:
            return []

    @staticmethod
    def obtenir_groupe_generique_par_id(groupe_id: int) -> Optional['GroupeGenerique']:
        """Obtient un groupe générique par son ID"""
        try:
            from app.models.academique import GroupeGenerique
            return GroupeGenerique.query.get(groupe_id)
        except Exception as e:
            return None

    @staticmethod
    def inscrire_etudiant_groupe_generique(etudiant_id: int, groupe_generique_id: int) -> bool:
        """Inscrit un étudiant à un groupe générique"""
        try:
            from app.models.academique import InscriptionGroupeGenerique, GroupeGenerique
            
            # Vérifier que l'étudiant et le groupe existent
            etudiant = Etudiant.query.get(etudiant_id)
            groupe = GroupeGenerique.query.get(groupe_generique_id)
            
            if not etudiant or not groupe:
                return False
            
            # Vérifier que l'étudiant n'est pas déjà inscrit
            inscription_existante = InscriptionGroupeGenerique.query.filter_by(
                etudiant_id=etudiant_id,
                groupe_generique_id=groupe_generique_id
            ).first()
            
            if inscription_existante:
                return False
            
            # Vérifier la capacité du groupe
            if groupe.nombre_etudiants >= groupe.capacite_max:
                return False
            
            # Créer l'inscription
            inscription = InscriptionGroupeGenerique(
                etudiant_id=etudiant_id,
                groupe_generique_id=groupe_generique_id
            )
            
            db.session.add(inscription)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def desinscrire_etudiant_groupe_generique(etudiant_id: int, groupe_generique_id: int) -> bool:
        """Désinscrit un étudiant d'un groupe générique"""
        try:
            from app.models.academique import InscriptionGroupeGenerique
            
            inscription = InscriptionGroupeGenerique.query.filter_by(
                etudiant_id=etudiant_id,
                groupe_generique_id=groupe_generique_id
            ).first()
            
            if not inscription:
                return False
            
            db.session.delete(inscription)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def lier_groupe_generique_ue(groupe_generique_id: int, unite_enseignement_id: int) -> bool:
        """Lie un groupe générique à une UE"""
        try:
            from app.models.academique import UtilisationGroupeUE, GroupeGenerique, UniteEnseignement
            
            # Vérifier que le groupe et l'UE existent
            groupe = GroupeGenerique.query.get(groupe_generique_id)
            ue = UniteEnseignement.query.get(unite_enseignement_id)
            
            if not groupe or not ue:
                return False
            
            # Vérifier que le lien n'existe pas déjà
            lien_existant = UtilisationGroupeUE.query.filter_by(
                groupe_generique_id=groupe_generique_id,
                unite_enseignement_id=unite_enseignement_id
            ).first()
            
            if lien_existant:
                return False
            
            # Créer le lien
            utilisation = UtilisationGroupeUE(
                groupe_generique_id=groupe_generique_id,
                unite_enseignement_id=unite_enseignement_id
            )
            
            db.session.add(utilisation)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def delier_groupe_generique_ue(groupe_generique_id: int, unite_enseignement_id: int) -> bool:
        """Délie un groupe générique d'une UE"""
        try:
            from app.models.academique import UtilisationGroupeUE
            
            utilisation = UtilisationGroupeUE.query.filter_by(
                groupe_generique_id=groupe_generique_id,
                unite_enseignement_id=unite_enseignement_id
            ).first()
            
            if not utilisation:
                return False
            
            db.session.delete(utilisation)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    @staticmethod
    def obtenir_groupes_generiques_par_ue(unite_enseignement_id: int) -> List['GroupeGenerique']:
        """Obtient tous les groupes génériques liés à une UE"""
        try:
            from app.models.academique import GroupeGenerique, UtilisationGroupeUE
            
            return db.session.query(GroupeGenerique).join(UtilisationGroupeUE).filter(
                UtilisationGroupeUE.unite_enseignement_id == unite_enseignement_id
            ).order_by(GroupeGenerique.code).all()
        except Exception as e:
            return []

    @staticmethod
    def obtenir_ues_par_groupe_generique(groupe_generique_id: int) -> List[UniteEnseignement]:
        """Obtient toutes les UE liées à un groupe générique"""
        try:
            from app.models.academique import UtilisationGroupeUE
            
            return db.session.query(UniteEnseignement).join(UtilisationGroupeUE).filter(
                UtilisationGroupeUE.groupe_generique_id == groupe_generique_id
            ).order_by(UniteEnseignement.code).all()
        except Exception as e:
            return []

    @staticmethod
    def obtenir_etudiants_groupe_generique(groupe_generique_id: int) -> List[Etudiant]:
        """Obtient tous les étudiants d'un groupe générique"""
        try:
            from app.models.academique import InscriptionGroupeGenerique
            
            return db.session.query(Etudiant).join(InscriptionGroupeGenerique).filter(
                InscriptionGroupeGenerique.groupe_generique_id == groupe_generique_id
            ).order_by(Etudiant.nom, Etudiant.prenom).all()
        except Exception as e:
            return []

    @staticmethod
    def creer_groupes_generiques_automatiques(nombre_groupes: int = 3, capacite_max: int = 30) -> List['GroupeGenerique']:
        """Crée automatiquement des groupes génériques"""
        try:
            from app.models.academique import GroupeGenerique
            
            groupes_crees = []
            lettres = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            
            for i in range(min(nombre_groupes, len(lettres))):
                nom = f"Groupe {lettres[i]}"
                code = f"G{lettres[i]}"
                
                # Vérifier si le groupe existe déjà
                groupe_existant = GroupeGenerique.query.filter_by(code=code).first()
                if groupe_existant:
                    continue
                
                groupe, success = ServiceAcademique.creer_groupe_generique(
                    nom=nom,
                    code=code,
                    capacite_max=capacite_max,
                    description=f"Groupe générique {lettres[i]} créé automatiquement"
                )
                
                if success:
                    groupes_crees.append(groupe)
            
            return groupes_crees
        except Exception as e:
            return []

    @staticmethod
    def lier_groupes_generiques_a_ue(unite_enseignement_id: int) -> bool:
        """Lie automatiquement tous les groupes génériques à une UE"""
        try:
            groupes_generiques = ServiceAcademique.obtenir_tous_groupes_generiques()
            
            for groupe in groupes_generiques:
                ServiceAcademique.lier_groupe_generique_ue(
                    groupe_generique_id=groupe.id,
                    unite_enseignement_id=unite_enseignement_id
                )
            
            return True
        except Exception as e:
            return False 