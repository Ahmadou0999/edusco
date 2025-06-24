"""
Routes d'authentification pour Edusco
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.authentification import bp

@bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        # TODO: Implémenter la logique de connexion
        flash('Fonctionnalité en cours de développement', 'info')
    
    return render_template('authentification/connexion.html')

@bp.route('/deconnexion')
@login_required
def deconnexion():
    """Déconnexion de l'utilisateur"""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('authentification.connexion')) 