"""
Routes enseignant pour Edusco
"""

from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.blueprints.enseignant import bp
from app.utils.decorateurs import enseignant_requis, utilisateur_actif_requis

@bp.route('/dashboard')
@login_required
@utilisateur_actif_requis
@enseignant_requis
def dashboard():
    """Tableau de bord enseignant"""
    return render_template('enseignant/dashboard.html')

@bp.route('/')
def index():
    """Page d'accueil enseignant"""
    return redirect(url_for('enseignant.dashboard'))

@bp.route('/mes-groupes')
@login_required
@utilisateur_actif_requis
@enseignant_requis
def mes_groupes():
    """Mes groupes d'enseignement"""
    return render_template('enseignant/mes_groupes.html')

@bp.route('/saisie-notes')
@login_required
@utilisateur_actif_requis
@enseignant_requis
def saisie_notes():
    """Saisie des notes"""
    return render_template('enseignant/saisie_notes.html') 