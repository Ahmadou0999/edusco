"""
Routes enseignant pour Edusco
"""

from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.blueprints.enseignant import bp

@bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord enseignant"""
    return render_template('enseignant/dashboard.html')

@bp.route('/')
def index():
    """Page d'accueil enseignant"""
    return redirect(url_for('enseignant.dashboard')) 