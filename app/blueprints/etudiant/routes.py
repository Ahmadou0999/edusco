from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from app.services.academique import ServiceAcademique
from app.services.pedagogique import ServicePedagogique
from app.services.notification import ServiceNotification


@bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    # Récupérer les informations de l'étudiant
    etudiant = service_academique.get_etudiant_par_utilisateur(current_user.id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé', 'error')
        return redirect(url_for('principal.accueil'))
    
    # Informations académiques
    informations_academiques = service_academique.get_informations_academiques_etudiant(etudiant.id)
    
    # Résultats académiques
    resultats = service_pedagogique.get_resultats_etudiant(etudiant.id)
    
    # Emploi du temps (si disponible)
    emploi_du_temps = service_pedagogique.get_emploi_du_temps_etudiant(etudiant.id)
    
    # Notifications récentes
    notifications = ServiceNotification.get_user_notifications(current_user.id, limit=5)
    
    return render_template('etudiant/dashboard.html',
                         etudiant=etudiant,
                         informations_academiques=informations_academiques,
                         resultats=resultats,
                         emploi_du_temps=emploi_du_temps,
                         notifications=notifications)


@bp.route('/notes')
@login_required
def notes():
    """Afficher les notes de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    etudiant = service_academique.get_etudiant_par_utilisateur(current_user.id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé', 'error')
        return redirect(url_for('principal.accueil'))
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    unite_id = request.args.get('unite_id', type=int)
    
    # Récupérer les notes selon les filtres
    notes = service_pedagogique.get_notes_etudiant(
        etudiant.id,
        annee_id=annee_id,
        semestre_id=semestre_id,
        unite_id=unite_id
    )
    
    # Options pour les filtres
    annees = service_academique.get_annees_academiques()
    semestres = service_pedagogique.get_semestres_actifs()
    unites = service_academique.get_unites_enseignement_actives()
    
    return render_template('etudiant/notes.html',
                         etudiant=etudiant,
                         notes=notes,
                         annees=annees,
                         semestres=semestres,
                         unites=unites)


@bp.route('/bulletin')
@login_required
def bulletin():
    """Afficher le bulletin de notes de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    etudiant = service_academique.get_etudiant_par_utilisateur(current_user.id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé', 'error')
        return redirect(url_for('principal.accueil'))
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    
    # Récupérer le bulletin selon les filtres
    bulletin_data = service_pedagogique.get_bulletin_etudiant(
        etudiant.id,
        annee_id=annee_id,
        semestre_id=semestre_id
    )
    
    # Options pour les filtres
    annees = service_academique.get_annees_academiques()
    semestres = service_pedagogique.get_semestres_actifs()
    
    return render_template('etudiant/bulletin.html',
                         etudiant=etudiant,
                         bulletin=bulletin_data,
                         annees=annees,
                         semestres=semestres)


@bp.route('/emploi-du-temps')
@login_required
def emploi_du_temps():
    """Afficher l'emploi du temps de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    etudiant = service_academique.get_etudiant_par_utilisateur(current_user.id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé', 'error')
        return redirect(url_for('principal.accueil'))
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    
    # Récupérer l'emploi du temps selon les filtres
    emploi_du_temps = service_pedagogique.get_emploi_du_temps_etudiant(
        etudiant.id,
        annee_id=annee_id,
        semestre_id=semestre_id
    )
    
    # Options pour les filtres
    annees = service_academique.get_annees_academiques()
    semestres = service_pedagogique.get_semestres_actifs()
    
    return render_template('etudiant/emploi_du_temps.html',
                         etudiant=etudiant,
                         emploi_du_temps=emploi_du_temps,
                         annees=annees,
                         semestres=semestres)


@bp.route('/absences')
@login_required
def absences():
    """Afficher les absences de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    etudiant = service_academique.get_etudiant_par_utilisateur(current_user.id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé', 'error')
        return redirect(url_for('principal.accueil'))
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    matiere_id = request.args.get('matiere_id', type=int)
    
    # Récupérer les absences selon les filtres
    absences = service_pedagogique.get_absences_etudiant(
        etudiant.id,
        annee_id=annee_id,
        semestre_id=semestre_id,
        matiere_id=matiere_id
    )
    
    # Options pour les filtres
    annees = service_academique.get_annees_academiques()
    semestres = service_pedagogique.get_semestres_actifs()
    matieres = service_academique.get_matieres_actives()
    
    return render_template('etudiant/absences.html',
                         etudiant=etudiant,
                         absences=absences,
                         annees=annees,
                         semestres=semestres,
                         matieres=matieres)


@bp.route('/profil')
@login_required
def profil():
    """Profil de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    etudiant = service_academique.get_etudiant_par_utilisateur(current_user.id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé', 'error')
        return redirect(url_for('principal.accueil'))
    
    # Informations académiques
    informations_academiques = service_academique.get_informations_academiques_etudiant(etudiant.id)
    
    # Résultats académiques
    resultats = service_pedagogique.get_resultats_etudiant(etudiant.id)
    
    return render_template('etudiant/profil.html',
                         etudiant=etudiant,
                         informations_academiques=informations_academiques,
                         resultats=resultats)


@bp.route('/notifications')
@login_required
def notifications():
    """Liste des notifications de l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.accueil'))
    
    notifications = ServiceNotification.get_user_notifications(current_user.id)
    
    return render_template('etudiant/notifications/liste.html',
                         notifications=notifications) 