"""
Modèle Utilisateur pour l'application Edusco
"""

from flask_login import UserMixin
from app.extensions import db, bcrypt
from datetime import datetime
from sqlalchemy import ForeignKey

class Utilisateur(db.Model, UserMixin):
    """Modèle utilisateur pour l'authentification"""
    
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='enseignant')  # administrateur, enseignant
    actif = db.Column(db.Boolean, default=True)
    email_verifie = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    
    # Champs pour les tokens
    token_reinitialisation = db.Column(db.String(255), unique=True)
    token_expiration = db.Column(db.DateTime)
    token_verification_email = db.Column(db.String(255), unique=True)
    
    notifications = db.relationship('Notification', back_populates='utilisateur', cascade='all, delete-orphan')
    
    # Relations avec les entités académiques
    enseignant = db.relationship('Enseignant', backref='utilisateur', uselist=False, foreign_keys='Enseignant.utilisateur_id')
    etudiant = db.relationship('Etudiant', backref='utilisateur', uselist=False, foreign_keys='Etudiant.utilisateur_id')
    
    def __init__(self, nom, prenom, email, mot_de_passe, role='enseignant', actif=True):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
        self.role = role
        self.actif = actif
    
    def verifier_mot_de_passe(self, mot_de_passe):
        """Vérifie si le mot de passe est correct"""
        return bcrypt.check_password_hash(self.mot_de_passe_hash, mot_de_passe)
    
    def __repr__(self):
        return f'<Utilisateur {self.email}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    titre = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    utilisateur = db.relationship('Utilisateur', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.titre} pour {self.utilisateur_id}>'

class Message(db.Model):
    """Modèle pour les messages internes"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    expediteur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    destinataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    sujet = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    lu = db.Column(db.Boolean, default=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    date_lecture = db.Column(db.DateTime)
    
    # Relations
    expediteur = db.relationship('Utilisateur', foreign_keys=[expediteur_id], backref='messages_envoyes')
    destinataire = db.relationship('Utilisateur', foreign_keys=[destinataire_id], backref='messages_recus')
    
    def __repr__(self):
        return f'<Message {self.sujet} de {self.expediteur_id} vers {self.destinataire_id}>' 