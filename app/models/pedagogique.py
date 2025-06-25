"""
Modèles pédagogiques pour Edusco
Contient les modèles pour la gestion pédagogique (notes, absences)
"""

from app.extensions import db
from datetime import datetime

class Note(db.Model):
    """Modèle pour les notes des étudiants"""
    
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    type_evaluation = db.Column(db.String(50), nullable=False)  # "Contrôle", "Examen", "TP", "Projet"
    note = db.Column(db.Float, nullable=False)  # note sur 20
    coefficient = db.Column(db.Float, nullable=False, default=1.0)
    date_evaluation = db.Column(db.Date, nullable=False)
    commentaire = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.etudiant.matricule} - {self.matiere.code} - {self.note}/20>'
    
    @property
    def note_ponderee(self):
        """Calcule la note pondérée"""
        return self.note * self.coefficient

class Absence(db.Model):
    """Modèle pour les absences des étudiants"""
    
    __tablename__ = 'absences'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    date_absence = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    motif = db.Column(db.String(200))  # "Maladie", "Famille", "Autre"
    justifiee = db.Column(db.Boolean, default=False)
    justificatif = db.Column(db.String(255))  # chemin vers le justificatif
    commentaire = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Absence {self.etudiant.matricule} - {self.date_absence} - {"Justifiée" if self.justifiee else "Non justifiée"}>'
    
    @property
    def duree_heures(self):
        """Calcule la durée de l'absence en heures"""
        from datetime import timedelta
        debut = datetime.combine(datetime.today(), self.heure_debut)
        fin = datetime.combine(datetime.today(), self.heure_fin)
        duree = fin - debut
        return duree.total_seconds() / 3600  # conversion en heures

class EmploiTemps(db.Model):
    """Modèle pour les emplois du temps"""
    
    __tablename__ = 'emplois_temps'
    
    id = db.Column(db.Integer, primary_key=True)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=False)
    matiere_id = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=False)
    jour_semaine = db.Column(db.Integer, nullable=False)  # 1=Lundi, 2=Mardi, ..., 7=Dimanche
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    salle = db.Column(db.String(50))
    type_cours = db.Column(db.String(50))  # "Cours", "TD", "TP"
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmploiTemps {self.groupe.code} - {self.matiere.code} - {self.jour_semaine}>'

class Délibération(db.Model):
    """Modèle pour les délibérations"""
    
    __tablename__ = 'deliberations'
    
    id = db.Column(db.Integer, primary_key=True)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestres.id'), nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    moyenne_generale = db.Column(db.Float, nullable=False)
    moyenne_ue = db.Column(db.Float, nullable=False)
    credits_obtenus = db.Column(db.Integer, nullable=False, default=0)
    credits_total = db.Column(db.Integer, nullable=False, default=0)
    decision = db.Column(db.String(50), nullable=False)  # "Admis", "Ajourné", "Redoublement"
    mention = db.Column(db.String(50))  # "Passable", "Assez bien", "Bien", "Très bien"
    commentaire = db.Column(db.Text)
    date_deliberation = db.Column(db.DateTime, default=datetime.utcnow)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Délibération {self.etudiant.matricule} - {self.semestre.nom} - {self.decision}>'
    
    @property
    def taux_reussite(self):
        """Calcule le taux de réussite en crédits"""
        if self.credits_total > 0:
            return (self.credits_obtenus / self.credits_total) * 100
        return 0 