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

def admin_required(f):
    """Décorateur pour exiger le rôle administrateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('authentification.connexion'))
        
        if current_user.role != 'admin':
            flash('Accès non autorisé. Droits administrateur requis.', 'error')
            return redirect(url_for('principal.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def enseignant_required(f):
    """Décorateur pour exiger le rôle enseignant"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('authentification.connexion'))
        
        if current_user.role not in ['administrateur', 'enseignant']:
            flash('Accès non autorisé. Droits enseignant requis.', 'error')
            return redirect(url_for('principal.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def etudiant_required(f):
    """Décorateur pour exiger le rôle étudiant"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('authentification.connexion'))
        
        if current_user.role not in ['administrateur', 'etudiant']:
            flash('Accès non autorisé. Droits étudiant requis.', 'error')
            return redirect(url_for('principal.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Décorateur pour exiger un ou plusieurs rôles spécifiques"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté pour accéder à cette page', 'error')
                return redirect(url_for('authentification.connexion'))
            
            if current_user.role not in roles:
                flash(f'Accès non autorisé. Rôles requis: {", ".join(roles)}', 'error')
                return redirect(url_for('principal.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission):
    """Décorateur pour exiger une permission spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté pour accéder à cette page', 'error')
                return redirect(url_for('authentification.connexion'))
            
            if not current_user.has_permission(permission):
                flash(f'Permission requise: {permission}', 'error')
                return redirect(url_for('principal.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def confirmation_required(message="Êtes-vous sûr de vouloir effectuer cette action ?"):
    """Décorateur pour exiger une confirmation avant l'action"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Cette fonctionnalité peut être implémentée avec JavaScript
            # pour afficher une boîte de dialogue de confirmation
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_action(action_name):
    """Décorateur pour logger les actions des utilisateurs"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Logique de journalisation des actions
            # À implémenter selon les besoins
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window=3600):
    """Décorateur pour limiter le taux de requêtes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Logique de limitation de taux
            # À implémenter selon les besoins
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(timeout=300):
    """Décorateur pour mettre en cache les réponses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Logique de mise en cache
            # À implémenter selon les besoins
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input(schema):
    """Décorateur pour valider les données d'entrée"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Logique de validation des données
            # À implémenter selon les besoins
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_errors(f):
    """Décorateur pour gérer les erreurs de manière centralisée"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Logique de gestion d'erreur
            flash(f'Une erreur est survenue: {str(e)}', 'error')
            return redirect(url_for('principal.dashboard'))
    return decorated_function

def require_https(f):
    """Décorateur pour exiger HTTPS en production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Logique de vérification HTTPS
        # À implémenter selon les besoins
        return f(*args, **kwargs)
    return decorated_function

def maintenance_mode(f):
    """Décorateur pour le mode maintenance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Logique de mode maintenance
        # À implémenter selon les besoins
        return f(*args, **kwargs)
    return decorated_function

# Décorateurs spécifiques au domaine académique
def enseignant_matiere_required(matiere_id_param='matiere_id'):
    """Décorateur pour vérifier qu'un enseignant enseigne une matière spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté pour accéder à cette page', 'error')
                return redirect(url_for('authentification.connexion'))
            
            if current_user.role == 'admin':
                return f(*args, **kwargs)
            
            if current_user.role != 'enseignant':
                flash('Accès non autorisé', 'error')
                return redirect(url_for('principal.dashboard'))
            
            # Vérifier que l'enseignant enseigne la matière
            matiere_id = kwargs.get(matiere_id_param)
            if matiere_id:
                from app.services.academique import ServiceAcademique
                service = ServiceAcademique()
                if not service.enseignant_enseigne_matiere(current_user.id, matiere_id):
                    flash('Vous n\'enseignez pas cette matière', 'error')
                    return redirect(url_for('enseignant.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def enseignant_groupe_required(groupe_id_param='groupe_id'):
    """Décorateur pour vérifier qu'un enseignant enseigne dans un groupe spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté pour accéder à cette page', 'error')
                return redirect(url_for('authentification.connexion'))
            
            if current_user.role == 'admin':
                return f(*args, **kwargs)
            
            if current_user.role != 'enseignant':
                flash('Accès non autorisé', 'error')
                return redirect(url_for('principal.dashboard'))
            
            # Vérifier que l'enseignant enseigne dans le groupe
            groupe_id = kwargs.get(groupe_id_param)
            if groupe_id:
                from app.services.academique import ServiceAcademique
                service = ServiceAcademique()
                if not service.enseignant_enseigne_groupe(current_user.id, groupe_id):
                    flash('Vous n\'enseignez pas dans ce groupe', 'error')
                    return redirect(url_for('enseignant.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def etudiant_propre_required(etudiant_id_param='etudiant_id'):
    """Décorateur pour vérifier qu'un étudiant accède à ses propres données"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté pour accéder à cette page', 'error')
                return redirect(url_for('authentification.connexion'))
            
            if current_user.role == 'admin':
                return f(*args, **kwargs)
            
            if current_user.role != 'etudiant':
                flash('Accès non autorisé', 'error')
                return redirect(url_for('principal.dashboard'))
            
            # Vérifier que l'étudiant accède à ses propres données
            etudiant_id = kwargs.get(etudiant_id_param)
            if etudiant_id and current_user.etudiant and current_user.etudiant.id != etudiant_id:
                flash('Vous ne pouvez accéder qu\'à vos propres données', 'error')
                return redirect(url_for('etudiant.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 