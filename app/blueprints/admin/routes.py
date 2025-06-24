"""
Routes d'administration pour Edusco
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.admin import bp
from app.utils.decorateurs import administrateur_requis, utilisateur_actif_requis

@bp.route('/dashboard')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def dashboard():
    """Tableau de bord administrateur"""
    return render_template('admin/dashboard.html')

@bp.route('/')
def index():
    """Page d'accueil admin"""
    return redirect(url_for('admin.dashboard'))

@bp.route('/utilisateurs')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def gestion_utilisateurs():
    """Gestion des utilisateurs"""
    return render_template('admin/utilisateurs.html')

@bp.route('/statistiques')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def statistiques():
    """Statistiques de l'institut"""
    return render_template('admin/statistiques.html') 