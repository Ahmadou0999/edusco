"""
Modèles de données pour l'application Edusco
Ce module contient tous les modèles SQLAlchemy
"""

from app.extensions import db

# Import des modèles
from app.models.utilisateur import Utilisateur
from app.models.academique import (
    AnneeAcademique, Semestre, UniteEnseignement, Matiere,
    Etudiant, Enseignant, Groupe, InscriptionGroupe
)
from app.models.pedagogique import (
    Note, Absence, EmploiTemps, Délibération
)

# Liste de tous les modèles pour les migrations
__all__ = [
    'Utilisateur',
    'AnneeAcademique',
    'Semestre', 
    'UniteEnseignement',
    'Matiere',
    'Etudiant',
    'Enseignant',
    'Groupe',
    'InscriptionGroupe',
    'Note',
    'Absence',
    'EmploiTemps',
    'Délibération'
] 