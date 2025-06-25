"""
Formulaires pour la gestion académique Edusco
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, IntegerField, FloatField, 
    DateField, SelectField, BooleanField, SubmitField, FileField
)
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError
from app.models.academique import Etudiant, Enseignant, UniteEnseignement, Matiere

class FormulaireAnneeAcademique(FlaskForm):
    """Formulaire pour les années académiques"""
    
    nom = StringField('Nom de l\'année', validators=[
        DataRequired(message='Le nom de l\'année est requis'),
        Length(min=4, max=20, message='Le nom doit contenir entre 4 et 20 caractères')
    ])
    
    date_debut = DateField('Date de début', validators=[
        DataRequired(message='La date de début est requise')
    ])
    
    date_fin = DateField('Date de fin', validators=[
        DataRequired(message='La date de fin est requise')
    ])
    
    active = BooleanField('Année active')
    
    bouton_sauvegarder = SubmitField('Sauvegarder')

class FormulaireSemestre(FlaskForm):
    """Formulaire pour les semestres"""
    
    nom = StringField('Nom du semestre', validators=[
        DataRequired(message='Le nom du semestre est requis'),
        Length(min=2, max=50, message='Le nom doit contenir entre 2 et 50 caractères')
    ])
    
    code = StringField('Code', validators=[
        DataRequired(message='Le code est requis'),
        Length(min=1, max=10, message='Le code doit contenir entre 1 et 10 caractères')
    ])
    
    date_debut = DateField('Date de début', validators=[
        DataRequired(message='La date de début est requise')
    ])
    
    date_fin = DateField('Date de fin', validators=[
        DataRequired(message='La date de fin est requise')
    ])
    
    actif = BooleanField('Semestre actif')
    
    bouton_sauvegarder = SubmitField('Sauvegarder')

class FormulaireUniteEnseignement(FlaskForm):
    """Formulaire pour les unités d'enseignement"""
    
    code = StringField('Code UE', validators=[
        DataRequired(message='Le code UE est requis'),
        Length(min=2, max=20, message='Le code doit contenir entre 2 et 20 caractères')
    ])
    
    nom = StringField('Nom de l\'UE', validators=[
        DataRequired(message='Le nom de l\'UE est requis'),
        Length(min=2, max=200, message='Le nom doit contenir entre 2 et 200 caractères')
    ])
    
    description = TextAreaField('Description')
    
    credits = IntegerField('Crédits', validators=[
        DataRequired(message='Le nombre de crédits est requis'),
        NumberRange(min=0, message='Le nombre de crédits doit être positif')
    ])
    
    coefficient = FloatField('Coefficient', validators=[
        DataRequired(message='Le coefficient est requis'),
        NumberRange(min=0.1, message='Le coefficient doit être positif')
    ])
    
    bouton_sauvegarder = SubmitField('Sauvegarder')
    
    def validate_code(self, code):
        """Vérifie que le code UE n'existe pas déjà"""
        ue = UniteEnseignement.query.filter_by(code=code.data).first()
        if ue:
            raise ValidationError('Ce code UE existe déjà. Veuillez choisir un autre code.')

class FormulaireMatiere(FlaskForm):
    """Formulaire pour les matières"""
    
    code = StringField('Code matière', validators=[
        DataRequired(message='Le code matière est requis'),
        Length(min=2, max=20, message='Le code doit contenir entre 2 et 20 caractères')
    ])
    
    nom = StringField('Nom de la matière', validators=[
        DataRequired(message='Le nom de la matière est requis'),
        Length(min=2, max=200, message='Le nom doit contenir entre 2 et 200 caractères')
    ])
    
    description = TextAreaField('Description')
    
    volume_horaire = IntegerField('Volume horaire (heures)', validators=[
        DataRequired(message='Le volume horaire est requis'),
        NumberRange(min=0, message='Le volume horaire doit être positif')
    ])
    
    coefficient = FloatField('Coefficient', validators=[
        DataRequired(message='Le coefficient est requis'),
        NumberRange(min=0.1, message='Le coefficient doit être positif')
    ])
    
    bouton_sauvegarder = SubmitField('Sauvegarder')

class FormulaireEtudiant(FlaskForm):
    """Formulaire pour les étudiants"""
    
    matricule = StringField('Matricule', validators=[
        DataRequired(message='Le matricule est requis'),
        Length(min=3, max=20, message='Le matricule doit contenir entre 3 et 20 caractères')
    ])
    
    nom = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=100, message='Le nom doit contenir entre 2 et 100 caractères')
    ])
    
    prenom = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=100, message='Le prénom doit contenir entre 2 et 100 caractères')
    ])
    
    date_naissance = DateField('Date de naissance', validators=[
        DataRequired(message='La date de naissance est requise')
    ])
    
    lieu_naissance = StringField('Lieu de naissance', validators=[
        Length(max=100, message='Le lieu de naissance ne peut pas dépasser 100 caractères')
    ])
    
    sexe = SelectField('Sexe', choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ], validators=[
        DataRequired(message='Le sexe est requis')
    ])
    
    adresse = TextAreaField('Adresse')
    
    telephone = StringField('Téléphone', validators=[
        Length(max=20, message='Le téléphone ne peut pas dépasser 20 caractères')
    ])
    
    email = StringField('Email', validators=[
        Email(message='Veuillez entrer un email valide')
    ])
    
    statut = SelectField('Statut', choices=[
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('diplômé', 'Diplômé'),
        ('abandon', 'Abandon')
    ], validators=[
        DataRequired(message='Le statut est requis')
    ])
    
    photo = FileField('Photo')
    
    bouton_sauvegarder = SubmitField('Sauvegarder')
    
    def validate_matricule(self, matricule):
        """Vérifie que le matricule n'existe pas déjà"""
        etudiant = Etudiant.query.filter_by(matricule=matricule.data).first()
        if etudiant:
            raise ValidationError('Ce matricule existe déjà. Veuillez choisir un autre matricule.')
    
    def validate_email(self, email):
        """Vérifie que l'email n'existe pas déjà"""
        if email.data:
            etudiant = Etudiant.query.filter_by(email=email.data).first()
            if etudiant:
                raise ValidationError('Cet email est déjà utilisé. Veuillez choisir un autre email.')

class FormulaireEnseignant(FlaskForm):
    """Formulaire pour les enseignants"""
    
    matricule = StringField('Matricule', validators=[
        DataRequired(message='Le matricule est requis'),
        Length(min=3, max=20, message='Le matricule doit contenir entre 3 et 20 caractères')
    ])
    
    nom = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=100, message='Le nom doit contenir entre 2 et 100 caractères')
    ])
    
    prenom = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=100, message='Le prénom doit contenir entre 2 et 100 caractères')
    ])
    
    date_naissance = DateField('Date de naissance', validators=[
        DataRequired(message='La date de naissance est requise')
    ])
    
    lieu_naissance = StringField('Lieu de naissance', validators=[
        Length(max=100, message='Le lieu de naissance ne peut pas dépasser 100 caractères')
    ])
    
    sexe = SelectField('Sexe', choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin')
    ], validators=[
        DataRequired(message='Le sexe est requis')
    ])
    
    adresse = TextAreaField('Adresse')
    
    telephone = StringField('Téléphone', validators=[
        Length(max=20, message='Le téléphone ne peut pas dépasser 20 caractères')
    ])
    
    email = StringField('Email', validators=[
        Email(message='Veuillez entrer un email valide')
    ])
    
    specialite = StringField('Spécialité', validators=[
        Length(max=200, message='La spécialité ne peut pas dépasser 200 caractères')
    ])
    
    grade = StringField('Grade', validators=[
        Length(max=50, message='Le grade ne peut pas dépasser 50 caractères')
    ])
    
    statut = SelectField('Statut', choices=[
        ('actif', 'Actif'),
        ('retraité', 'Retraité'),
        ('démissionné', 'Démissionné')
    ], validators=[
        DataRequired(message='Le statut est requis')
    ])
    
    date_embauche = DateField('Date d\'embauche', validators=[
        DataRequired(message='La date d\'embauche est requise')
    ])
    
    photo = FileField('Photo')
    
    bouton_sauvegarder = SubmitField('Sauvegarder')
    
    def validate_matricule(self, matricule):
        """Vérifie que le matricule n'existe pas déjà"""
        enseignant = Enseignant.query.filter_by(matricule=matricule.data).first()
        if enseignant:
            raise ValidationError('Ce matricule existe déjà. Veuillez choisir un autre matricule.')
    
    def validate_email(self, email):
        """Vérifie que l'email n'existe pas déjà"""
        if email.data:
            enseignant = Enseignant.query.filter_by(email=email.data).first()
            if enseignant:
                raise ValidationError('Cet email est déjà utilisé. Veuillez choisir un autre email.')

class FormulaireGroupe(FlaskForm):
    """Formulaire pour les groupes"""
    
    nom = StringField('Nom du groupe', validators=[
        DataRequired(message='Le nom du groupe est requis'),
        Length(min=2, max=50, message='Le nom doit contenir entre 2 et 50 caractères')
    ])
    
    code = StringField('Code du groupe', validators=[
        DataRequired(message='Le code du groupe est requis'),
        Length(min=1, max=20, message='Le code doit contenir entre 1 et 20 caractères')
    ])
    
    capacite_max = IntegerField('Capacité maximale', validators=[
        DataRequired(message='La capacité maximale est requise'),
        NumberRange(min=1, message='La capacité doit être positive')
    ])
    
    description = TextAreaField('Description')
    
    bouton_sauvegarder = SubmitField('Sauvegarder') 