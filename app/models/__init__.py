"""
Modèles de données pour l'application Edusco
Ce module contient tous les modèles SQLAlchemy
"""

from app.extensions import db

# Import des modèles utilisateur
from .utilisateur import Utilisateur, Notification

# Import des modèles académiques
from .academique import (
    AnneeAcademique, Semestre, UniteEnseignement, Matiere,
    Etudiant, Enseignant, Groupe, InscriptionGroupe
)

# Import des modèles pédagogiques
from .pedagogique import (
    Note, Absence, EmploiDuTemps, Deliberation, ResultatDeliberation,
    ajouter_relations_pedagogiques
)

# Ajouter les relations pédagogiques aux modèles existants
ajouter_relations_pedagogiques()

# Liste de tous les modèles pour les migrations
__all__ = [
    # Modèles utilisateur
    'Utilisateur',
    'Notification',
    
    # Modèles académiques
    'AnneeAcademique',
    'Semestre', 
    'UniteEnseignement',
    'Matiere',
    'Etudiant',
    'Enseignant',
    'Groupe',
    'InscriptionGroupe',
    
    # Modèles pédagogiques
    'Note',
    'Absence',
    'EmploiDuTemps',
    'Deliberation',
    'ResultatDeliberation'
] 