"""
Modèles pédagogiques pour Edusco
Contient les modèles pour la gestion pédagogique (notes, absences)
"""

from app.extensions import db
from datetime import datetime, date
from sqlalchemy.orm import relationship

class Note(db.Model):
    """Modèle pour les notes des étudiants"""
    
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    
    # Types d'évaluation
    TYPE_CONTROLE = 'controle'
    TYPE_EXAMEN = 'examen'
    TYPE_TP = 'tp'
    TYPE_PROJET = 'projet'
    TYPE_ORAL = 'oral'
    
    type_evaluation = db.Column(db.String(20), nullable=False, default=TYPE_CONTROLE)
    note = db.Column(db.Float, nullable=False)  # Note sur 20
    coefficient = db.Column(db.Float, default=1.0)
    commentaire = db.Column(db.Text)
    date_evaluation = db.Column(db.Date, nullable=False, default=date.today)
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Validation des notes
    validee = db.Column(db.Boolean, default=False)
    validee_par = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    date_validation = db.Column(db.DateTime)
    commentaire_validation = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Note {self.etudiant.nom if self.etudiant else "N/A"} - {self.matiere.nom if self.matiere else "N/A"}: {self.note}/20>'
    
    @property
    def note_ponderee(self):
        """Retourne la note pondérée par le coefficient"""
        return self.note * self.coefficient
    
    @property
    def est_validee(self):
        """Vérifie si la note est dans une plage valide"""
        return 0 <= self.note <= 20

class Absence(db.Model):
    """Modèle pour les absences des étudiants"""
    
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    
    date_absence = db.Column(db.Date, nullable=False, default=date.today)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    motif = db.Column(db.String(100))  # Maladie, motif personnel, etc.
    justifiee = db.Column(db.Boolean, default=False)
    justificatif = db.Column(db.String(255))  # Chemin vers le fichier justificatif
    commentaire = db.Column(db.Text)
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Absence {self.etudiant.nom if self.etudiant else "N/A"} - {self.date_absence}>'
    
    @property
    def duree_heures(self):
        """Calcule la durée de l'absence en heures"""
        debut = datetime.combine(date.today(), self.heure_debut)
        fin = datetime.combine(date.today(), self.heure_fin)
        return (fin - debut).total_seconds() / 3600

class EmploiDuTemps(db.Model):
    """Modèle pour les emplois du temps"""
    
    __tablename__ = 'emplois_du_temps'
    
    id = db.Column(db.Integer, primary_key=True)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    salle = db.Column(db.String(50))
    
    # Jours de la semaine (0=Lundi, 6=Dimanche)
    jour = db.Column(db.Integer, nullable=False)  # 0-6
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    
    # Période (semestre, année)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestres.id'), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<EDT {self.groupe.nom if self.groupe else "N/A"} - {self.matiere.nom if self.matiere else "N/A"} - {self.jour_semaine}>'
    
    @property
    def jour_semaine(self):
        """Retourne le nom du jour de la semaine"""
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return jours[self.jour] if 0 <= self.jour < 7 else 'Inconnu'
    
    @property
    def duree_heures(self):
        """Calcule la durée du cours en heures"""
        debut = datetime.combine(date.today(), self.heure_debut)
        fin = datetime.combine(date.today(), self.heure_fin)
        return (fin - debut).total_seconds() / 3600

class Deliberation(db.Model):
    """Modèle pour les délibérations"""
    
    __tablename__ = 'deliberations'
    
    id = db.Column(db.Integer, primary_key=True)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestres.id'), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=False)
    
    # Statuts de délibération
    STATUT_EN_COURS = 'en_cours'
    STATUT_VALIDEE = 'validee'
    STATUT_REJETEE = 'rejetee'
    
    statut = db.Column(db.String(20), default=STATUT_EN_COURS)
    date_deliberation = db.Column(db.Date, nullable=False, default=date.today)
    date_validation = db.Column(db.Date)
    commentaire = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Deliberation {self.groupe.nom if self.groupe else "N/A"} - {self.semestre.nom if self.semestre else "N/A"}>'

class ResultatDeliberation(db.Model):
    """Modèle pour les résultats de délibération par étudiant"""
    __tablename__ = 'resultats_deliberation'
    
    id = db.Column(db.Integer, primary_key=True)
    deliberation_id = db.Column(db.Integer, db.ForeignKey('deliberations.id'), nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    
    # Résultats
    moyenne_generale = db.Column(db.Float, nullable=False)
    credits_obtenus = db.Column(db.Integer, default=0)
    credits_totaux = db.Column(db.Integer, default=0)
    
    # Décision
    DECISION_ADMIS = 'admis'
    DECISION_ADMIS_AVEC_RESERVE = 'admis_reserve'
    DECISION_ECHEC = 'echec'
    DECISION_REDOUBLEMENT = 'redoublement'
    
    decision = db.Column(db.String(20), nullable=False)
    commentaire = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Resultat {self.etudiant.nom if self.etudiant else "N/A"} - {self.decision}>'
    
    @property
    def taux_reussite(self):
        """Calcule le taux de réussite en crédits"""
        if self.credits_totaux > 0:
            return (self.credits_obtenus / self.credits_totaux) * 100
        return 0.0

# Mise à jour des modèles existants pour ajouter les relations
def ajouter_relations_pedagogiques():
    """Ajoute les relations pédagogiques aux modèles existants"""
    from app.models.academique import Etudiant, Matiere, Groupe, Enseignant, Semestre
    
    # Relations pour Etudiant
    Etudiant.notes = relationship('Note', backref='etudiant', cascade='all, delete-orphan')
    Etudiant.absences = relationship('Absence', backref='etudiant', cascade='all, delete-orphan')
    Etudiant.resultats_deliberation = relationship('ResultatDeliberation', backref='etudiant', cascade='all, delete-orphan')
    
    # Relations pour Matiere
    Matiere.notes = relationship('Note', backref='matiere', cascade='all, delete-orphan')
    Matiere.absences = relationship('Absence', backref='matiere', cascade='all, delete-orphan')
    Matiere.emplois_du_temps = relationship('EmploiDuTemps', backref='matiere', cascade='all, delete-orphan')
    
    # Relations pour Groupe
    Groupe.notes = relationship('Note', backref='groupe', cascade='all, delete-orphan')
    Groupe.absences = relationship('Absence', backref='groupe', cascade='all, delete-orphan')
    Groupe.emplois_du_temps = relationship('EmploiDuTemps', backref='groupe', cascade='all, delete-orphan')
    Groupe.deliberations = relationship('Deliberation', backref='groupe', cascade='all, delete-orphan')
    
    # Relations pour Enseignant
    Enseignant.notes_saisies = relationship('Note', backref='enseignant', cascade='all, delete-orphan')
    Enseignant.emplois_du_temps = relationship('EmploiDuTemps', backref='enseignant', cascade='all, delete-orphan')
    Enseignant.absences_saisies = relationship('Absence', backref='enseignant', cascade='all, delete-orphan')
    
    # Relations pour Semestre
    Semestre.emplois_du_temps = relationship('EmploiDuTemps', backref='semestre', cascade='all, delete-orphan')
    Semestre.deliberations = relationship('Deliberation', backref='semestre', cascade='all, delete-orphan')
    
    # Relations pour Deliberation
    Deliberation.resultats = relationship('ResultatDeliberation', backref='deliberation', cascade='all, delete-orphan') 