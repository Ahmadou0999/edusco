"""
Routes d'authentification pour Edusco
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.authentification import bp
from app.forms.authentification import FormulaireConnexion, FormulaireInscription, FormulaireChangementMotDePasse
from app.services.authentification import ServiceAuthentification
from app.utils.decorateurs import administrateur_requis

@bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Page de connexion"""
    if current_user.is_authenticated:
        # Rediriger selon le rôle
        if current_user.role == 'administrateur':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'enseignant':
            return redirect(url_for('enseignant.dashboard'))
    
    formulaire = FormulaireConnexion()
    
    if formulaire.validate_on_submit():
        email = formulaire.email.data
        mot_de_passe = formulaire.mot_de_passe.data
        se_souvenir = formulaire.se_souvenir.data
        
        # Authentifier l'utilisateur
        utilisateur, authentification_reussie = ServiceAuthentification.authentifier_utilisateur(
            email, mot_de_passe
        )
        
        if authentification_reussie:
            # Connecter l'utilisateur
            if ServiceAuthentification.connecter_utilisateur(utilisateur, se_souvenir):
                flash(f'Bienvenue {utilisateur.prenom} {utilisateur.nom} !', 'success')
                
                # Rediriger selon le rôle
                if utilisateur.role == 'administrateur':
                    return redirect(url_for('admin.dashboard'))
                elif utilisateur.role == 'enseignant':
                    return redirect(url_for('enseignant.dashboard'))
            else:
                flash('Erreur lors de la connexion. Veuillez réessayer.', 'error')
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('authentification/connexion.html', formulaire=formulaire)

@bp.route('/deconnexion')
@login_required
def deconnexion():
    """Déconnexion de l'utilisateur"""
    if ServiceAuthentification.deconnecter_utilisateur():
        flash('Vous avez été déconnecté avec succès.', 'success')
    else:
        flash('Erreur lors de la déconnexion.', 'error')
    
    return redirect(url_for('authentification.connexion'))

@bp.route('/inscription', methods=['GET', 'POST'])
@administrateur_requis
def inscription():
    """Page d'inscription (réservée aux administrateurs)"""
    formulaire = FormulaireInscription()
    
    if formulaire.validate_on_submit():
        nom = formulaire.nom.data
        prenom = formulaire.prenom.data
        email = formulaire.email.data
        mot_de_passe = formulaire.mot_de_passe.data
        role = formulaire.role.data
        
        # Créer l'utilisateur
        utilisateur, creation_reussie = ServiceAuthentification.creer_utilisateur(
            nom, prenom, email, mot_de_passe, role
        )
        
        if creation_reussie:
            flash(f'Utilisateur {prenom} {nom} créé avec succès !', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Erreur lors de la création de l\'utilisateur.', 'error')
    
    return render_template('authentification/inscription.html', formulaire=formulaire)

@bp.route('/changer-mot-de-passe', methods=['GET', 'POST'])
@login_required
def changer_mot_de_passe():
    """Page de changement de mot de passe"""
    formulaire = FormulaireChangementMotDePasse()
    
    if formulaire.validate_on_submit():
        mot_de_passe_actuel = formulaire.mot_de_passe_actuel.data
        nouveau_mot_de_passe = formulaire.nouveau_mot_de_passe.data
        
        # Vérifier le mot de passe actuel
        if current_user.verifier_mot_de_passe(mot_de_passe_actuel):
            # Changer le mot de passe
            if ServiceAuthentification.changer_mot_de_passe(current_user, nouveau_mot_de_passe):
                flash('Votre mot de passe a été changé avec succès !', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Erreur lors du changement de mot de passe.', 'error')
        else:
            flash('Mot de passe actuel incorrect.', 'error')
    
    return render_template('authentification/changer_mot_de_passe.html', formulaire=formulaire)

@bp.route('/profil')
@login_required
def profil():
    """Page de profil utilisateur"""
    return render_template('authentification/profil.html') 