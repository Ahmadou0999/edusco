"""
Routes d'authentification pour Edusco
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.utilisateur import Utilisateur, Notification
from app.services.authentification import ServiceAuthentification
from app.forms.authentification import ConnexionForm, InscriptionForm, ChangementMotDePasseForm
from app import db
from datetime import datetime, timedelta
import secrets

bp = Blueprint('authentification', __name__)

@bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Page de connexion"""
    if current_user.is_authenticated:
        # Rediriger selon le rôle
        if current_user.role == 'administrateur':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'enseignant':
            return redirect(url_for('enseignant.dashboard'))
        elif current_user.role == 'etudiant':
            return redirect(url_for('etudiant.dashboard'))
        else:
            return redirect(url_for('principal.dashboard'))
    
    form = ConnexionForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        service_auth = ServiceAuthentification()
        
        try:
            utilisateur, authentifie = service_auth.authentifier_utilisateur(
                email=form.email.data,
                mot_de_passe=form.mot_de_passe.data
            )
            
            if authentifie and utilisateur:
                login_user(utilisateur, remember=form.se_souvenir.data)
                # Redirection prioritaire vers next si présent et sûr
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                # Sinon, rediriger selon le rôle
                if utilisateur.role == 'administrateur':
                    return redirect(url_for('admin.dashboard'))
                elif utilisateur.role == 'enseignant':
                    return redirect(url_for('enseignant.dashboard'))
                elif utilisateur.role == 'etudiant':
                    return redirect(url_for('etudiant.dashboard'))
                else:
                    return redirect(url_for('principal.dashboard'))
            else:
                flash('Email ou mot de passe incorrect', 'error')
                
        except Exception as e:
            flash(f'Erreur lors de la connexion: {str(e)}', 'error')
    
    return render_template('authentification/connexion.html', form=form)

@bp.route('/deconnexion')
@login_required
def deconnexion():
    """Déconnexion de l'utilisateur"""
    logout_user()
    session.clear()
    flash('Vous avez été déconnecté avec succès', 'success')
    return redirect(url_for('principal.accueil'))

@bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Page d'inscription - DÉSACTIVÉE pour la sécurité"""
    flash('L\'inscription publique est désactivée pour des raisons de sécurité. Veuillez contacter l\'administrateur.', 'warning')
    return redirect(url_for('authentification.connexion'))

@bp.route('/mot-de-passe-oublie', methods=['GET', 'POST'])
def mot_de_passe_oublie():
    """Demande de réinitialisation de mot de passe"""
    if current_user.is_authenticated:
        return redirect(url_for('principal.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Veuillez saisir votre email', 'error')
            return render_template('authentification/mot_de_passe_oublie.html')
        
        service_auth = ServiceAuthentification()
        
        try:
            # Générer un token de réinitialisation
            token = service_auth.generer_token_reinitialisation(email)
            
            if token:
                # Envoyer l'email de réinitialisation
                service_auth.envoyer_email_reinitialisation(email, token)
                flash('Un email de réinitialisation a été envoyé à votre adresse email', 'success')
            else:
                flash('Aucun compte trouvé avec cet email', 'error')
                
        except Exception as e:
            flash(f'Erreur lors de l\'envoi de l\'email: {str(e)}', 'error')
    
    return render_template('authentification/mot_de_passe_oublie.html')

@bp.route('/reinitialiser-mot-de-passe/<token>', methods=['GET', 'POST'])
def reinitialiser_mot_de_passe(token):
    """Réinitialisation du mot de passe avec token"""
    if current_user.is_authenticated:
        return redirect(url_for('principal.dashboard'))
    
    service_auth = ServiceAuthentification()
    
    # Vérifier la validité du token
    utilisateur = service_auth.verifier_token_reinitialisation(token)
    
    if not utilisateur:
        flash('Token invalide ou expiré', 'error')
        return redirect(url_for('authentification.connexion'))
    
    if request.method == 'POST':
        mot_de_passe = request.form.get('mot_de_passe')
        confirmation = request.form.get('confirmation')
        
        if not mot_de_passe or not confirmation:
            flash('Veuillez saisir le mot de passe et sa confirmation', 'error')
            return render_template('authentification/reinitialiser_mot_de_passe.html')
        
        if mot_de_passe != confirmation:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('authentification/reinitialiser_mot_de_passe.html')
        
        if len(mot_de_passe) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('authentification/reinitialiser_mot_de_passe.html')
        
        try:
            # Mettre à jour le mot de passe
            service_auth.reinitialiser_mot_de_passe(utilisateur.id, mot_de_passe)
            
            # Invalider le token
            service_auth.invalider_token_reinitialisation(token)
            
            flash('Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('authentification.connexion'))
            
        except Exception as e:
            flash(f'Erreur lors de la réinitialisation: {str(e)}', 'error')
    
    return render_template('authentification/reinitialiser_mot_de_passe.html')

@bp.route('/changer-mot-de-passe', methods=['GET', 'POST'])
@login_required
def changer_mot_de_passe():
    """Changer le mot de passe de l'utilisateur connecté"""
    form = ChangementMotDePasseForm()
    
    if form.validate_on_submit():
        service_auth = ServiceAuthentification()
        
        try:
            # Vérifier l'ancien mot de passe
            if not service_auth.verifier_mot_de_passe(current_user.id, form.ancien_mot_de_passe.data):
                flash('Ancien mot de passe incorrect', 'error')
                return render_template('principal/changer_mot_de_passe.html', form=form)
            
            # Changer le mot de passe
            service_auth.changer_mot_de_passe(current_user.id, form.nouveau_mot_de_passe.data)
            
            flash('Mot de passe changé avec succès', 'success')
            return redirect(url_for('principal.profil'))
            
        except Exception as e:
            flash(f'Erreur lors du changement de mot de passe: {str(e)}', 'error')
    
    return render_template('principal/changer_mot_de_passe.html', form=form)

@bp.route('/verifier-email/<token>')
def verifier_email(token):
    """Vérification de l'email avec token"""
    service_auth = ServiceAuthentification()
    
    try:
        utilisateur = service_auth.verifier_email_avec_token(token)
        
        if utilisateur:
            flash('Email vérifié avec succès', 'success')
        else:
            flash('Token invalide ou expiré', 'error')
            
    except Exception as e:
        flash(f'Erreur lors de la vérification: {str(e)}', 'error')
    
    return redirect(url_for('authentification.connexion'))

@bp.route('/renvoyer-verification')
@login_required
def renvoyer_verification():
    """Renvoyer l'email de vérification"""
    service_auth = ServiceAuthentification()
    
    try:
        if not current_user.email_verifie:
            service_auth.renvoyer_email_verification(current_user.id)
            flash('Email de vérification renvoyé', 'success')
        else:
            flash('Votre email est déjà vérifié', 'info')
            
    except Exception as e:
        flash(f'Erreur lors de l\'envoi: {str(e)}', 'error')
    
    return redirect(url_for('principal.profil'))

@bp.route('/verifier-session')
@login_required
def verifier_session():
    """Vérifier la validité de la session"""
    return jsonify({
        'authenticated': True,
        'user_id': current_user.id,
        'role': current_user.role,
        'email': current_user.email
    })

@bp.route('/prolonger-session')
@login_required
def prolonger_session():
    """Prolonger la session de l'utilisateur"""
    # Cette route peut être appelée périodiquement par JavaScript
    # pour maintenir la session active
    return jsonify({'success': True})

# Routes pour la gestion des comptes (admin uniquement)
@bp.route('/liste-utilisateurs')
@login_required
def liste_utilisateurs():
    """Liste des utilisateurs (admin uniquement)"""
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.dashboard'))
    
    service_auth = ServiceAuthentification()
    utilisateurs = service_auth.get_tous_utilisateurs()
    
    return render_template('authentification/liste_utilisateurs.html', 
                         utilisateurs=utilisateurs)

@bp.route('/activer-utilisateur/<int:user_id>', methods=['POST'])
@login_required
def activer_utilisateur(user_id):
    """Activer un utilisateur (admin uniquement)"""
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.dashboard'))
    
    service_auth = ServiceAuthentification()
    
    try:
        service_auth.activer_utilisateur(user_id)
        flash('Utilisateur activé avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de l\'activation: {str(e)}', 'error')
    
    return redirect(url_for('authentification.liste_utilisateurs'))

@bp.route('/desactiver-utilisateur/<int:user_id>', methods=['POST'])
@login_required
def desactiver_utilisateur(user_id):
    """Désactiver un utilisateur (admin uniquement)"""
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.dashboard'))
    
    service_auth = ServiceAuthentification()
    
    try:
        service_auth.desactiver_utilisateur(user_id)
        flash('Utilisateur désactivé avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de la désactivation: {str(e)}', 'error')
    
    return redirect(url_for('authentification.liste_utilisateurs'))

@bp.route('/changer-role/<int:user_id>', methods=['POST'])
@login_required
def changer_role(user_id):
    """Changer le rôle d'un utilisateur (admin uniquement)"""
    if current_user.role != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.dashboard'))
    
    nouveau_role = request.form.get('role')
    
    if not nouveau_role or nouveau_role not in ['admin', 'enseignant', 'etudiant']:
        flash('Rôle invalide', 'error')
        return redirect(url_for('authentification.liste_utilisateurs'))
    
    service_auth = ServiceAuthentification()
    
    try:
        service_auth.changer_role_utilisateur(user_id, nouveau_role)
        flash('Rôle modifié avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors du changement de rôle: {str(e)}', 'error')
    
    return redirect(url_for('authentification.liste_utilisateurs')) 