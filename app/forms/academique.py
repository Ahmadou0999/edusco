"""
Formulaires pour la gestion académique Edusco
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, IntegerField, FloatField, 
    DateField, SelectField, BooleanField, SubmitField, FileField, PasswordField
)
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError, EqualTo
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
    
    annee_academique_id = SelectField('Année académique', coerce=int, validators=[
        DataRequired(message='L\'année académique est requise')
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
    
    semestre_id = SelectField('Semestre', coerce=int, validators=[
        DataRequired(message='Le semestre est requis')
    ])
    
    bouton_sauvegarder = SubmitField('Sauvegarder')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ue_id = kwargs.get('obj').id if kwargs.get('obj') else None
    
    def validate_code(self, code):
        """Vérifie que le code UE n'existe pas déjà (sauf pour la modification)"""
        ue = UniteEnseignement.query.filter_by(code=code.data).first()
        if ue and (not self.ue_id or ue.id != self.ue_id):
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
    
    unite_enseignement_id = SelectField('Unité d\'enseignement', coerce=int, validators=[
        DataRequired(message='L\'unité d\'enseignement est requise')
    ])
    
    enseignant_id = SelectField('Enseignant', coerce=lambda x: int(x) if x else None, validators=[])
    
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
    
    def validate_telephone(self, telephone):
        """Valide le format du numéro de téléphone"""
        if telephone.data and telephone.data.strip():
            # Nettoyer le numéro de téléphone (garder seulement les chiffres)
            tel_clean = ''.join(filter(str.isdigit, telephone.data))
            if len(tel_clean) < 8 or len(tel_clean) > 15:
                raise ValidationError('Le numéro de téléphone doit contenir entre 8 et 15 chiffres')
            # Vérifier qu'il ne contient que des chiffres, espaces, tirets et parenthèses
            import re
            if not re.match(r'^[\d\s\-\(\)]+$', telephone.data):
                raise ValidationError('Le numéro de téléphone ne peut contenir que des chiffres, espaces, tirets et parenthèses')

    email = StringField('Email', validators=[
        Email(message='Veuillez entrer un email valide')
    ])
    
    mot_de_passe = PasswordField('Mot de passe (optionnel)', validators=[
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    confirmer_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[])
    
    def validate_confirmer_mot_de_passe(self, confirmer_mot_de_passe):
        """Valide que les mots de passe correspondent si un mot de passe est fourni"""
        if self.mot_de_passe.data and confirmer_mot_de_passe.data != self.mot_de_passe.data:
            raise ValidationError('Les mots de passe ne correspondent pas')
    
    statut = SelectField('Statut', choices=[
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('diplômé', 'Diplômé'),
        ('abandon', 'Abandon')
    ], validators=[
        DataRequired(message='Le statut est requis')
    ])
    
    annee_academique_id = SelectField('Année académique', coerce=int, validators=[
        DataRequired(message='L\'année académique est requise')
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
    
    mot_de_passe = PasswordField('Mot de passe', validators=[
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    confirmer_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[
        EqualTo('mot_de_passe', message='Les mots de passe ne correspondent pas')
    ])
    
    specialite = StringField('Spécialité', validators=[
        Length(max=200, message='La spécialité ne peut pas dépasser 200 caractères')
    ])
    
    grade = StringField('Grade', validators=[
        Length(max=50, message='Le grade ne peut pas dépasser 50 caractères')
    ])
    
    statut = SelectField('Statut', choices=[
        ('actif', 'Actif'),
        ('retraite', 'Retraite'),
        ('demissionne', 'Demissionne')
    ], validators=[
        DataRequired(message='Le statut est requis')
    ])
    
    date_embauche = DateField('Date d\'embauche', validators=[
        DataRequired(message='La date d\'embauche est requise')
    ])
    
    photo = FileField('Photo')
    
    bouton_sauvegarder = SubmitField('Sauvegarder')
    
    def __init__(self, *args, **kwargs):
        self.enseignant_existant = kwargs.pop('enseignant_existant', None)
        super(FormulaireEnseignant, self).__init__(*args, **kwargs)
    
    def validate_matricule(self, matricule):
        """Vérifie que le matricule n'existe pas déjà (sauf pour l'enseignant en cours de modification)"""
        enseignant = Enseignant.query.filter_by(matricule=matricule.data).first()
        if enseignant and (not self.enseignant_existant or enseignant.id != self.enseignant_existant.id):
            raise ValidationError('Ce matricule existe déjà. Veuillez choisir un autre matricule.')
    
    def validate_email(self, email):
        """Vérifie que l'email n'existe pas déjà (sauf pour l'enseignant en cours de modification)"""
        if email.data:
            enseignant = Enseignant.query.filter_by(email=email.data).first()
            if enseignant and (not self.enseignant_existant or enseignant.id != self.enseignant_existant.id):
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
    
    unite_enseignement_id = SelectField('Unité d\'enseignement', coerce=int, validators=[
        DataRequired(message='L\'unité d\'enseignement est requise')
    ])
    
    enseignant_responsable_id = SelectField('Enseignant responsable', coerce=lambda x: int(x) if x else None, validators=[])
    
    description = TextAreaField('Description')
    
    bouton_sauvegarder = SubmitField('Sauvegarder') 

# ==================== FORMULAIRES POUR GROUPES GÉNÉRIQUES ====================

class FormulaireGroupeGenerique(FlaskForm):
    """Formulaire pour les groupes génériques"""
    
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
    
    enseignant_responsable_id = SelectField('Enseignant responsable', coerce=lambda x: int(x) if x else None, validators=[])
    
    description = TextAreaField('Description')
    
    bouton_sauvegarder = SubmitField('Sauvegarder')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groupe_id = kwargs.get('obj').id if kwargs.get('obj') else None
    
    def validate_code(self, code):
        """Vérifie que le code du groupe générique n'existe pas déjà (sauf pour la modification)"""
        from app.models.academique import GroupeGenerique
        groupe = GroupeGenerique.query.filter_by(code=code.data).first()
        if groupe and (not self.groupe_id or groupe.id != self.groupe_id):
            raise ValidationError('Ce code de groupe existe déjà. Veuillez choisir un autre code.')

class FormulaireUtilisationGroupeUE(FlaskForm):
    """Formulaire pour lier un groupe générique à une UE"""
    
    groupe_generique_id = SelectField('Groupe générique', coerce=int, validators=[
        DataRequired(message='Le groupe générique est requis')
    ])
    
    unite_enseignement_id = SelectField('Unité d\'enseignement', coerce=int, validators=[
        DataRequired(message='L\'unité d\'enseignement est requise')
    ])
    
    bouton_sauvegarder = SubmitField('Lier le groupe à l\'UE') 