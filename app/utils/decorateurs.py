"""
Décorateurs pour la protection des routes selon les rôles
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required
from app.services.authentification import ServiceAuthentification

def role_requis(role):
    """
    Décorateur pour vérifier le rôle de l'utilisateur
    
    Args:
        role (str): Rôle requis pour accéder à la route
        
    Returns:
        function: Fonction décorée
    """
    def decorateur(f):
        @wraps(f)
        def fonction_decoree(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('authentification.connexion'))
            
            if not ServiceAuthentification.verifier_permissions(current_user, role):
                flash('Vous n\'avez pas les permissions nécessaires pour accéder à cette page.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return fonction_decoree
    return decorateur

def administrateur_requis(f):
    """
    Décorateur pour les routes réservées aux administrateurs
    
    Args:
        f: Fonction à décorer
        
    Returns:
        function: Fonction décorée
    """
    @wraps(f)
    def fonction_decoree(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('authentification.connexion'))
        
        if current_user.role != 'administrateur':
            flash('Accès réservé aux administrateurs.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return fonction_decoree

def enseignant_requis(f):
    """
    Décorateur pour les routes réservées aux enseignants
    
    Args:
        f: Fonction à décorer
        
    Returns:
        function: Fonction décorée
    """
    @wraps(f)
    def fonction_decoree(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('authentification.connexion'))
        
        if current_user.role not in ['enseignant', 'administrateur']:
            flash('Accès réservé aux enseignants.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return fonction_decoree

def utilisateur_actif_requis(f):
    """
    Décorateur pour vérifier que l'utilisateur est actif
    
    Args:
        f: Fonction à décorer
        
    Returns:
        function: Fonction décorée
    """
    @wraps(f)
    def fonction_decoree(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('authentification.connexion'))
        
        if not current_user.actif:
            flash('Votre compte a été désactivé. Contactez l\'administrateur.', 'error')
            return redirect(url_for('authentification.deconnexion'))
        
        return f(*args, **kwargs)
    return fonction_decoree 