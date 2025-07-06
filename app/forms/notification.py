from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Length, Email
from app.models.academique import Groupe, Etudiant
from app.models.utilisateur import Utilisateur

class FormulaireNotification(FlaskForm):
    """Formulaire pour l'envoi de notifications"""
    
    titre = StringField('Titre', validators=[
        DataRequired(message='Le titre est requis'),
        Length(min=3, max=100, message='Le titre doit contenir entre 3 et 100 caractères')
    ])
    
    contenu = TextAreaField('Contenu', validators=[
        DataRequired(message='Le contenu est requis'),
        Length(min=10, max=1000, message='Le contenu doit contenir entre 10 et 1000 caractères')
    ])
    
    type_notification = SelectField('Type de notification', choices=[
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('success', 'Succès'),
        ('error', 'Erreur'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired(message='Le type de notification est requis')])
    
    destinataires = SelectField('Destinataires', choices=[
        ('tous', 'Tous les utilisateurs'),
        ('etudiants', 'Tous les étudiants'),
        ('enseignants', 'Tous les enseignants'),
        ('admin', 'Administrateurs uniquement'),
        ('groupe', 'Groupe spécifique')
    ], validators=[DataRequired(message='Les destinataires sont requis')])
    
    groupe_id = SelectField('Groupe', coerce=int, validators=[])
    
    envoyer_email = BooleanField('Envoyer par email')
    
    def __init__(self, *args, **kwargs):
        super(FormulaireNotification, self).__init__(*args, **kwargs)
        
        # Remplir les choix de groupes
        groupes = Groupe.query.all()
        self.groupe_id.choices = [(0, 'Sélectionner un groupe')] + [(g.id, g.nom) for g in groupes]
        
        # Validation conditionnelle pour le groupe
        if self.destinataires.data == 'groupe':
            self.groupe_id.validators = [DataRequired(message='Veuillez sélectionner un groupe')] 