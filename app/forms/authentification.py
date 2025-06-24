"""
Formulaires d'authentification pour Edusco
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.utilisateur import Utilisateur

class FormulaireConnexion(FlaskForm):
    """Formulaire de connexion"""
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ])
    
    mot_de_passe = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    se_souvenir = BooleanField('Se souvenir de moi')
    
    bouton_connexion = SubmitField('Se connecter')

class FormulaireInscription(FlaskForm):
    """Formulaire d'inscription (pour les administrateurs)"""
    
    nom = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=50, message='Le nom doit contenir entre 2 et 50 caractères')
    ])
    
    prenom = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=50, message='Le prénom doit contenir entre 2 et 50 caractères')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ])
    
    mot_de_passe = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    confirmer_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='La confirmation du mot de passe est requise'),
        EqualTo('mot_de_passe', message='Les mots de passe ne correspondent pas')
    ])
    
    role = StringField('Rôle', validators=[
        DataRequired(message='Le rôle est requis')
    ])
    
    bouton_inscription = SubmitField('Créer le compte')
    
    def validate_email(self, email):
        """Vérifie que l'email n'existe pas déjà"""
        utilisateur = Utilisateur.query.filter_by(email=email.data).first()
        if utilisateur:
            raise ValidationError('Cet email est déjà utilisé. Veuillez choisir un autre email.')

class FormulaireChangementMotDePasse(FlaskForm):
    """Formulaire de changement de mot de passe"""
    
    mot_de_passe_actuel = PasswordField('Mot de passe actuel', validators=[
        DataRequired(message='Le mot de passe actuel est requis')
    ])
    
    nouveau_mot_de_passe = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le nouveau mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    confirmer_nouveau_mot_de_passe = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(message='La confirmation du mot de passe est requise'),
        EqualTo('nouveau_mot_de_passe', message='Les mots de passe ne correspondent pas')
    ])
    
    bouton_changer = SubmitField('Changer le mot de passe')

class FormulaireRecuperationMotDePasse(FlaskForm):
    """Formulaire de récupération de mot de passe"""
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ])
    
    bouton_recuperer = SubmitField('Envoyer le lien de récupération') 