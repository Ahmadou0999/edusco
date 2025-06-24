"""
Routes principales pour Edusco
"""

from flask import render_template, redirect, url_for
from app.blueprints.principal import bp

@bp.route('/')
def accueil():
    """Page d'accueil publique"""
    return render_template('principal/accueil.html')

@bp.route('/apropos')
def apropos():
    """Page à propos"""
    return render_template('principal/apropos.html') 