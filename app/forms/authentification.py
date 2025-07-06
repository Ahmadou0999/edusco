"""
Formulaires d'authentification pour Edusco
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.utilisateur import Utilisateur

class ConnexionForm(FlaskForm):
    """Formulaire de connexion"""
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Format d\'email invalide')
    ])
    mot_de_passe = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis')
    ])
    se_souvenir = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class InscriptionForm(FlaskForm):
    """Formulaire d'inscription"""
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
        Email(message='Format d\'email invalide'),
        Length(max=120, message='L\'email ne peut pas dépasser 120 caractères')
    ])
    mot_de_passe = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    confirmation_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='La confirmation du mot de passe est requise'),
        EqualTo('mot_de_passe', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('S\'inscrire')

    def validate_email(self, email):
        """Vérifier que l'email n'existe pas déjà"""
        utilisateur = Utilisateur.query.filter_by(email=email.data).first()
        if utilisateur:
            raise ValidationError('Cet email est déjà utilisé')

class ChangementMotDePasseForm(FlaskForm):
    """Formulaire de changement de mot de passe"""
    ancien_mot_de_passe = PasswordField('Ancien mot de passe', validators=[
        DataRequired(message='L\'ancien mot de passe est requis')
    ])
    nouveau_mot_de_passe = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le nouveau mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    confirmation_nouveau_mot_de_passe = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(message='La confirmation du nouveau mot de passe est requise'),
        EqualTo('nouveau_mot_de_passe', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('Changer le mot de passe')

class MotDePasseOublieForm(FlaskForm):
    """Formulaire de mot de passe oublié"""
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Format d\'email invalide')
    ])
    submit = SubmitField('Envoyer le lien de réinitialisation')

class ReinitialisationMotDePasseForm(FlaskForm):
    """Formulaire de réinitialisation de mot de passe"""
    mot_de_passe = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    confirmation_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='La confirmation du mot de passe est requise'),
        EqualTo('mot_de_passe', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('Réinitialiser le mot de passe')

class ProfilUtilisateurForm(FlaskForm):
    """Formulaire de modification du profil utilisateur"""
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
        Email(message='Format d\'email invalide'),
        Length(max=120, message='L\'email ne peut pas dépasser 120 caractères')
    ])
    telephone = StringField('Téléphone', validators=[
        Length(max=20, message='Le numéro de téléphone ne peut pas dépasser 20 caractères')
    ])
    adresse = StringField('Adresse', validators=[
        Length(max=200, message='L\'adresse ne peut pas dépasser 200 caractères')
    ])
    submit = SubmitField('Mettre à jour le profil')

    def __init__(self, utilisateur_actuel=None, *args, **kwargs):
        super(ProfilUtilisateurForm, self).__init__(*args, **kwargs)
        self.utilisateur_actuel = utilisateur_actuel

    def validate_email(self, email):
        """Vérifier que l'email n'existe pas déjà (sauf pour l'utilisateur actuel)"""
        if self.utilisateur_actuel and email.data == self.utilisateur_actuel.email:
            return
        utilisateur = Utilisateur.query.filter_by(email=email.data).first()
        if utilisateur:
            raise ValidationError('Cet email est déjà utilisé')

class GestionUtilisateurForm(FlaskForm):
    """Formulaire de gestion des utilisateurs (admin)"""
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
        Email(message='Format d\'email invalide'),
        Length(max=120, message='L\'email ne peut pas dépasser 120 caractères')
    ])
    mot_de_passe = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    role = SelectField('Rôle', choices=[
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur')
    ], validators=[
        DataRequired(message='Le rôle est requis')
    ])
    actif = BooleanField('Compte actif')
    submit = SubmitField('Enregistrer')

    def __init__(self, utilisateur_existant=None, *args, **kwargs):
        super(GestionUtilisateurForm, self).__init__(*args, **kwargs)
        self.utilisateur_existant = utilisateur_existant
        
        # Si c'est une modification, le mot de passe n'est pas obligatoire
        if utilisateur_existant:
            self.mot_de_passe.validators = [
                Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
            ]

    def validate_email(self, email):
        """Vérifier que l'email n'existe pas déjà (sauf pour l'utilisateur existant)"""
        if self.utilisateur_existant and email.data == self.utilisateur_existant.email:
            return
        utilisateur = Utilisateur.query.filter_by(email=email.data).first()
        if utilisateur:
            raise ValidationError('Cet email est déjà utilisé')

class RechercheUtilisateurForm(FlaskForm):
    """Formulaire de recherche d'utilisateurs"""
    terme_recherche = StringField('Rechercher', validators=[
        DataRequired(message='Le terme de recherche est requis')
    ])
    role = SelectField('Rôle', choices=[
        ('', 'Tous les rôles'),
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur')
    ])
    statut = SelectField('Statut', choices=[
        ('', 'Tous les statuts'),
        ('actif', 'Actif'),
        ('inactif', 'Inactif')
    ])
    submit = SubmitField('Rechercher')

class FiltreUtilisateurForm(FlaskForm):
    """Formulaire de filtrage des utilisateurs"""
    role = SelectField('Rôle', choices=[
        ('', 'Tous les rôles'),
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur')
    ])
    statut = SelectField('Statut', choices=[
        ('', 'Tous les statuts'),
        ('actif', 'Actif'),
        ('inactif', 'Inactif')
    ])
    email_verifie = SelectField('Email vérifié', choices=[
        ('', 'Tous'),
        ('oui', 'Oui'),
        ('non', 'Non')
    ])
    submit = SubmitField('Filtrer') 