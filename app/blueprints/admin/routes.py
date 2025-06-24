"""
Routes d'administration pour Edusco
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.admin import bp

@bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord administrateur"""
    return render_template('admin/dashboard.html')

@bp.route('/')
def index():
    """Page d'accueil admin"""
    return redirect(url_for('admin.dashboard')) 