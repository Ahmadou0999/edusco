"""
Modèles de données académiques pour Edusco
Contient les modèles pour la gestion académique
"""

from app.extensions import db
from datetime import datetime

class AnneeAcademique(db.Model):
    """Modèle pour les années académiques"""
    
    __tablename__ = 'annees_academiques'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(20), nullable=False, unique=True)  # ex: "2023-2024"
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    semestres = db.relationship('Semestre', backref='annee_academique', lazy=True, cascade='all, delete-orphan')
    etudiants = db.relationship('Etudiant', backref='annee_academique', lazy=True)
    
    def __repr__(self):
        return f'<AnneeAcademique {self.nom}>'

class Semestre(db.Model):
    """Modèle pour les semestres"""
    
    __tablename__ = 'semestres'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # ex: "Semestre 1", "Semestre 2"
    code = db.Column(db.String(10), nullable=False)  # ex: "S1", "S2"
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    actif = db.Column(db.Boolean, default=False)
    annee_academique_id = db.Column(db.Integer, db.ForeignKey('annees_academiques.id'), nullable=False)
    
    # Relations
    unites_enseignement = db.relationship('UniteEnseignement', backref='semestre', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Semestre {self.nom} - {self.annee_academique.nom}>'

class UniteEnseignement(db.Model):
    """Modèle pour les unités d'enseignement"""
    
    __tablename__ = 'unites_enseignement'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)  # ex: "UE101", "UE102"
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False, default=0)
    coefficient = db.Column(db.Float, nullable=False, default=1.0)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestres.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    matieres = db.relationship('Matiere', backref='unite_enseignement', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UniteEnseignement {self.code} - {self.nom}>'

class Matiere(db.Model):
    """Modèle pour les matières"""
    
    __tablename__ = 'matieres'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)  # ex: "MAT101", "PHY101"
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    volume_horaire = db.Column(db.Integer, nullable=False, default=0)  # en heures
    coefficient = db.Column(db.Float, nullable=False, default=1.0)
    unite_enseignement_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    notes = db.relationship('Note', backref='matiere', lazy=True, cascade='all, delete-orphan')
    absences = db.relationship('Absence', backref='matiere', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Matiere {self.code} - {self.nom}>'

class Etudiant(db.Model):
    """Modèle pour les étudiants"""
    
    __tablename__ = 'etudiants'
    
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), nullable=False, unique=True)  # ex: "2023-001", "2023-002"
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    lieu_naissance = db.Column(db.String(100))
    sexe = db.Column(db.String(10), nullable=False)  # "M" ou "F"
    adresse = db.Column(db.Text)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    photo = db.Column(db.String(255))  # chemin vers la photo
    statut = db.Column(db.String(20), default='actif')  # actif, suspendu, diplômé, abandon
    annee_academique_id = db.Column(db.Integer, db.ForeignKey('annees_academiques.id'), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    notes = db.relationship('Note', backref='etudiant', lazy=True, cascade='all, delete-orphan')
    absences = db.relationship('Absence', backref='etudiant', lazy=True, cascade='all, delete-orphan')
    inscriptions_groupes = db.relationship('InscriptionGroupe', backref='etudiant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Etudiant {self.matricule} - {self.prenom} {self.nom}>'
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class Enseignant(db.Model):
    """Modèle pour les enseignants"""
    
    __tablename__ = 'enseignants'
    
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), nullable=False, unique=True)  # ex: "ENS001", "ENS002"
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    lieu_naissance = db.Column(db.String(100))
    sexe = db.Column(db.String(10), nullable=False)  # "M" ou "F"
    adresse = db.Column(db.Text)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    photo = db.Column(db.String(255))  # chemin vers la photo
    specialite = db.Column(db.String(200))  # domaine de spécialisation
    grade = db.Column(db.String(50))  # ex: "Maître Assistant", "Professeur"
    statut = db.Column(db.String(20), default='actif')  # actif, retraité, démissionné
    date_embauche = db.Column(db.Date, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    matieres = db.relationship('Matiere', backref='enseignant', lazy=True)
    groupes = db.relationship('Groupe', backref='enseignant_responsable', lazy=True)
    
    def __repr__(self):
        return f'<Enseignant {self.matricule} - {self.prenom} {self.nom}>'
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class Groupe(db.Model):
    """Modèle pour les groupes d'étudiants"""
    
    __tablename__ = 'groupes'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)  # ex: "Groupe A", "Groupe B"
    code = db.Column(db.String(20), nullable=False, unique=True)  # ex: "GA", "GB"
    capacite_max = db.Column(db.Integer, nullable=False, default=30)
    description = db.Column(db.Text)
    enseignant_responsable_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'))
    unite_enseignement_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    inscriptions = db.relationship('InscriptionGroupe', backref='groupe', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Groupe {self.code} - {self.nom}>'
    
    @property
    def nombre_etudiants(self):
        return len(self.inscriptions)

class InscriptionGroupe(db.Model):
    """Modèle pour les inscriptions des étudiants aux groupes"""
    
    __tablename__ = 'inscriptions_groupes'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    groupe_id = db.Column(db.Integer, db.ForeignKey('groupes.id'), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Contrainte unique pour éviter les doublons
    __table_args__ = (db.UniqueConstraint('etudiant_id', 'groupe_id', name='_etudiant_groupe_uc'),)
    
    def __repr__(self):
        return f'<InscriptionGroupe {self.etudiant.matricule} - {self.groupe.code}>' 