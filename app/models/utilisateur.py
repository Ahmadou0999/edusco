"""
Modèle Utilisateur pour l'application Edusco
"""

from flask_login import UserMixin
from app.extensions import db, bcrypt
from datetime import datetime

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
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    
    def __init__(self, email, nom, prenom, mot_de_passe, role='enseignant'):
        self.email = email
        self.nom = nom
        self.prenom = prenom
        self.mot_de_passe_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
        self.role = role
    
    def verifier_mot_de_passe(self, mot_de_passe):
        """Vérifie si le mot de passe est correct"""
        return bcrypt.check_password_hash(self.mot_de_passe_hash, mot_de_passe)
    
    def __repr__(self):
        return f'<Utilisateur {self.email}>' 