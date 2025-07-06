"""
Routes pour le module enseignant
Gestion des cours, notes, absences, emplois du temps
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.pedagogique import ServicePedagogique
from app.services.academique import ServiceAcademique
from app.models.academique import Etudiant, Matiere, Groupe, Semestre
from app.models.pedagogique import Note, Absence, EmploiDuTemps
from app.utils.decorateurs import enseignant_required
from app.extensions import db
from datetime import datetime, date, time
import json
from app.services.notification import ServiceNotification

from . import bp  # Utilise le blueprint du module

@bp.route('/dashboard')
@login_required
@enseignant_required
def dashboard():
    """Tableau de bord de l'enseignant"""
    enseignant = current_user.enseignant
    if not enseignant:
        flash("Votre compte n'est pas lié à un profil enseignant. Contactez l'administrateur.", "error")
        return redirect(url_for('principal.dashboard'))
    service_pedagogique = ServicePedagogique()
    
    # Statistiques
    stats = {
        'total_matieres': len(enseignant.matieres),
        'total_groupes': len(enseignant.groupes),
        'total_etudiants': sum(len(groupe.etudiants) for groupe in enseignant.groupes),
        'notes_saisies': service_pedagogique.compter_notes_par_enseignant(enseignant.id),
        'absences_saisies': service_pedagogique.compter_absences_par_enseignant(enseignant.id)
    }
    
    # Activités récentes
    activites_recentes = service_pedagogique.get_activites_recentes_enseignant(enseignant.id)
    
    return render_template('enseignant/dashboard.html', 
                         stats=stats, 
                         activites_recentes=activites_recentes)

@bp.route('/')
def index():
    """Page d'accueil enseignant"""
    return redirect(url_for('enseignant.dashboard'))

@bp.route('/notes')
@login_required
@enseignant_required
def notes():
    """Liste des notes de l'enseignant"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Filtres
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    
    notes = service_pedagogique.get_notes_par_enseignant_paginees(
        enseignant.id, 
        page=page,
        per_page=per_page,
        matiere_id=matiere_id,
        groupe_id=groupe_id,
        semestre_id=semestre_id
    )
    
    # Options pour les filtres
    matieres = enseignant.matieres
    groupes = enseignant.groupes
    semestres = service_pedagogique.get_semestres_actifs()
    
    return render_template('enseignant/notes.html', 
                         notes=notes,
                         matieres=matieres,
                         groupes=groupes,
                         semestres=semestres)

@bp.route('/saisir-notes', methods=['GET', 'POST'])
@login_required
@enseignant_required
def saisir_notes():
    """Saisir les notes pour une matière et un groupe"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    service_academique = ServiceAcademique()
    
    if request.method == 'POST':
        data = request.get_json()
        matiere_id = data.get('matiere_id')
        groupe_id = data.get('groupe_id')
        type_evaluation = data.get('type_evaluation')
        date_evaluation = data.get('date_evaluation')
        commentaire = data.get('commentaire', '')
        notes_data = data.get('notes', [])
        
        try:
            # Récupérer la matière pour déduire le semestre
            matiere = service_academique.get_matiere_par_id(matiere_id)
            if not matiere or not matiere.unite_enseignement or not matiere.unite_enseignement.semestre:
                return jsonify({'success': False, 'message': 'Matière ou semestre non trouvé'}), 400
            
            semestre_id = matiere.unite_enseignement.semestre.id
            
            # Vérifier que l'enseignant enseigne cette matière dans ce groupe
            if not service_academique.enseignant_enseigne_matiere_groupe(
                enseignant.id, matiere_id, groupe_id):
                return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
            
            # Ajouter les informations d'évaluation à chaque note
            for note in notes_data:
                note['type_evaluation'] = type_evaluation
                note['date_evaluation'] = date_evaluation
                note['commentaire'] = commentaire
            
            # Sauvegarder les notes
            service_pedagogique.sauvegarder_notes(
                enseignant.id, matiere_id, groupe_id, semestre_id, notes_data
            )
            
            return jsonify({'success': True, 'message': 'Notes sauvegardées avec succès'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # GET - Afficher le formulaire
    # Récupérer toutes les matières de l'enseignant
    matieres = enseignant.matieres if enseignant.matieres else []
    
    # Si l'enseignant n'a pas de matières assignées, récupérer toutes les matières actives
    if not matieres:
        matieres = service_academique.get_matieres_actives()
        print(f"⚠️  Enseignant {enseignant.nom_complet} n'a pas de matières assignées, récupération de toutes les matières actives: {len(matieres)}")
    else:
        print(f"✅ Enseignant {enseignant.nom_complet} a {len(matieres)} matières assignées")
    
    # Récupérer tous les groupes
    groupes = enseignant.groupes if enseignant.groupes else []
    
    # Si l'enseignant n'a pas de groupes assignés, récupérer tous les groupes
    if not groupes:
        groupes = service_academique.obtenir_tous_groupes()
        print(f"⚠️  Enseignant {enseignant.nom_complet} n'a pas de groupes assignés, récupération de tous les groupes: {len(groupes)}")
    else:
        print(f"✅ Enseignant {enseignant.nom_complet} a {len(groupes)} groupes assignés")
    
    return render_template('enseignant/saisir_notes.html',
                         matieres=matieres,
                         groupes=groupes)

@bp.route('/valider-notes', methods=['POST'])
@login_required
@enseignant_required
def valider_notes():
    """Valider les notes saisies (les rendre définitives)"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    service_academique = ServiceAcademique()
    
    data = request.get_json()
    matiere_id = data.get('matiere_id')
    groupe_id = data.get('groupe_id')
    type_evaluation = data.get('type_evaluation')
    date_evaluation = data.get('date_evaluation')
    commentaire = data.get('commentaire', '')
    notes_data = data.get('notes', [])
    
    try:
        # Récupérer la matière pour déduire le semestre
        matiere = service_academique.get_matiere_par_id(matiere_id)
        if not matiere or not matiere.unite_enseignement or not matiere.unite_enseignement.semestre:
            return jsonify({'success': False, 'message': 'Matière ou semestre non trouvé'}), 400
        
        semestre_id = matiere.unite_enseignement.semestre.id
        
        # Vérifier que l'enseignant enseigne cette matière dans ce groupe
        if not service_academique.enseignant_enseigne_matiere_groupe(
            enseignant.id, matiere_id, groupe_id):
            return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
        
        # Valider les notes (les rendre définitives)
        service_pedagogique.valider_notes(
            enseignant.id, matiere_id, groupe_id, semestre_id, notes_data, type_evaluation, date_evaluation, commentaire
        )
        
        return jsonify({'success': True, 'message': 'Notes validées avec succès'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de la validation: {str(e)}'}), 500

@bp.route('/get-etudiants-groupe/<int:groupe_id>')
@login_required
@enseignant_required
def get_etudiants_groupe(groupe_id):
    """Récupérer les étudiants d'un groupe pour la saisie de notes"""
    enseignant = current_user.enseignant
    service_academique = ServiceAcademique()
    
    # Vérifier que l'enseignant a accès à ce groupe
    # Si l'enseignant n'a pas de groupes assignés, il peut accéder à tous les groupes
    # (cohérent avec la logique du formulaire de saisie de notes)
    groupes_enseignant = enseignant.groupes if enseignant.groupes else []
    
    if groupes_enseignant:
        # Si l'enseignant a des groupes assignés, vérifier qu'il a accès à ce groupe
        if not any(g.id == groupe_id for g in groupes_enseignant):
            return jsonify({'error': 'Accès non autorisé à ce groupe'}), 403
    else:
        # Si l'enseignant n'a pas de groupes assignés, vérifier que le groupe existe
        groupe = service_academique.get_groupe_par_id(groupe_id)
        if not groupe:
            return jsonify({'error': 'Groupe non trouvé'}), 404
    
    etudiants = service_academique.get_etudiants_par_groupe(groupe_id)
    return jsonify([{
        'id': e.id,
        'nom': e.nom,
        'prenom': e.prenom,
        'matricule': e.matricule
    } for e in etudiants])

@bp.route('/modifier-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
@enseignant_required
def modifier_note(note_id):
    """Modifier une note existante"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    note = service_pedagogique.get_note_par_id(note_id)
    
    if not note or note.enseignant_id != enseignant.id:
        flash('Note non trouvée ou accès non autorisé', 'error')
        return redirect(url_for('enseignant.notes'))
    
    if request.method == 'POST':
        try:
            nouvelle_note = float(request.form['note'])
            appreciation = request.form.get('appreciation', '')
            
            service_pedagogique.modifier_note(note_id, nouvelle_note, appreciation)
            flash('Note modifiée avec succès', 'success')
            return redirect(url_for('enseignant.notes'))
            
        except ValueError:
            flash('Valeur de note invalide', 'error')
        except Exception as e:
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('enseignant/modifier_note.html', note=note)

@bp.route('/notes/supprimer/<int:note_id>', methods=['POST'])
@login_required
@enseignant_required
def supprimer_note(note_id):
    enseignant = current_user.enseignant
    note = Note.query.get(note_id)
    if not note or note.enseignant_id != enseignant.id:
        flash('Note non trouvée ou accès non autorisé', 'error')
        return redirect(url_for('enseignant.notes'))
    db.session.delete(note)
    db.session.commit()
    flash('Note supprimée avec succès', 'success')
    return redirect(url_for('enseignant.notes'))

@bp.route('/rapport-notes')
@login_required
@enseignant_required
def rapport_notes():
    """Rapport des notes par matière et groupe"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    # Filtres
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    
    rapport = service_pedagogique.generer_rapport_notes_enseignant(
        enseignant.id,
        matiere_id=matiere_id,
        groupe_id=groupe_id,
        semestre_id=semestre_id
    )
    
    # Options pour les filtres
    matieres = enseignant.matieres
    groupes = enseignant.groupes
    semestres = service_pedagogique.get_semestres_actifs()
    
    return render_template('enseignant/rapport_notes.html',
                         rapport=rapport,
                         matieres=matieres,
                         groupes=groupes,
                         semestres=semestres)

@bp.route('/absences')
@login_required
@enseignant_required
def absences():
    """Liste des absences saisies par l'enseignant"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Filtres
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    absences = service_pedagogique.get_absences_par_enseignant_paginees(
        enseignant.id,
        page=page,
        per_page=per_page,
        matiere_id=matiere_id,
        groupe_id=groupe_id,
        date_debut=date_debut,
        date_fin=date_fin
    )
    
    # Options pour les filtres
    matieres = enseignant.matieres
    groupes = enseignant.groupes
    
    return render_template('enseignant/absences.html',
                         absences=absences,
                         matieres=matieres,
                         groupes=groupes)

@bp.route('/saisir-absences', methods=['GET', 'POST'])
@login_required
@enseignant_required
def saisir_absences():
    """Saisir les absences pour une matière et un groupe"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    service_academique = ServiceAcademique()
    
    if request.method == 'POST':
        data = request.get_json()
        matiere_id = data.get('matiere_id')
        groupe_id = data.get('groupe_id')
        date_absence = data.get('date_absence')
        heure_debut = data.get('heure_debut')
        heure_fin = data.get('heure_fin')
        motif = data.get('motif', '')
        absences_data = data.get('absences', [])
        
        try:
            # Vérifier que l'enseignant enseigne cette matière dans ce groupe
            if not service_academique.enseignant_enseigne_matiere_groupe(
                enseignant.id, matiere_id, groupe_id):
                return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
            
            # Sauvegarder les absences
            service_pedagogique.sauvegarder_absences(
                enseignant.id, matiere_id, groupe_id, date_absence, absences_data, heure_debut, heure_fin, motif
            )
            
            return jsonify({'success': True, 'message': 'Absences sauvegardées avec succès'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # GET - Afficher le formulaire
    # Récupérer toutes les matières de l'enseignant
    matieres = enseignant.matieres if enseignant.matieres else []
    
    # Si l'enseignant n'a pas de matières assignées, récupérer toutes les matières actives
    if not matieres:
        matieres = service_academique.get_matieres_actives()
        print(f"⚠️  Enseignant {enseignant.nom_complet} n'a pas de matières assignées, récupération de toutes les matières actives: {len(matieres)}")
    else:
        print(f"✅ Enseignant {enseignant.nom_complet} a {len(matieres)} matières assignées")
    
    # Récupérer tous les groupes
    groupes = enseignant.groupes if enseignant.groupes else []
    
    # Si l'enseignant n'a pas de groupes assignés, récupérer tous les groupes
    if not groupes:
        groupes = service_academique.obtenir_tous_groupes()
        print(f"⚠️  Enseignant {enseignant.nom_complet} n'a pas de groupes assignés, récupération de tous les groupes: {len(groupes)}")
    else:
        print(f"✅ Enseignant {enseignant.nom_complet} a {len(groupes)} groupes assignés")
    
    return render_template('enseignant/saisir_absences.html',
                         matieres=matieres,
                         groupes=groupes)

@bp.route('/modifier-absence/<int:absence_id>', methods=['GET', 'POST'])
@login_required
@enseignant_required
def modifier_absence(absence_id):
    """Modifier une absence existante"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    absence = service_pedagogique.get_absence_par_id(absence_id)
    
    if not absence or absence.enseignant_id != enseignant.id:
        flash('Absence non trouvée ou accès non autorisé', 'error')
        return redirect(url_for('enseignant.absences'))
    
    if request.method == 'POST':
        try:
            justifiee = 'justifiee' in request.form
            motif = request.form.get('motif', '')
            
            service_pedagogique.modifier_absence(absence_id, justifiee, motif)
            flash('Absence modifiée avec succès', 'success')
            return redirect(url_for('enseignant.absences'))
            
        except Exception as e:
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('enseignant/modifier_absence.html', absence=absence)

@bp.route('/absences/supprimer/<int:absence_id>', methods=['POST'])
@login_required
@enseignant_required
def supprimer_absence(absence_id):
    enseignant = current_user.enseignant
    absence = Absence.query.get(absence_id)
    if not absence:
        flash('Absence non trouvée', 'error')
        return redirect(url_for('enseignant.absences'))
    groupe = Groupe.query.get(absence.groupe_id)
    if not groupe or groupe.enseignant_id != enseignant.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('enseignant.absences'))
    db.session.delete(absence)
    db.session.commit()
    flash('Absence supprimée avec succès', 'success')
    return redirect(url_for('enseignant.absences'))

@bp.route('/rapport-absences')
@login_required
@enseignant_required
def rapport_absences():
    """Rapport des absences par matière et groupe"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    # Filtres
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    rapport = service_pedagogique.generer_rapport_absences_enseignant(
        enseignant.id,
        matiere_id=matiere_id,
        groupe_id=groupe_id,
        date_debut=date_debut,
        date_fin=date_fin
    )
    
    # Options pour les filtres
    matieres = enseignant.matieres
    groupes = enseignant.groupes
    
    return render_template('enseignant/rapport_absences.html',
                         rapport=rapport,
                         matieres=matieres,
                         groupes=groupes)

@bp.route('/emploi-du-temps')
@login_required
@enseignant_required
def emploi_du_temps():
    """Afficher l'emploi du temps de l'enseignant"""
    enseignant = current_user.enseignant
    service_pedagogique = ServicePedagogique()
    
    emploi_du_temps = service_pedagogique.obtenir_emploi_du_temps_enseignant(enseignant.id)
    
    return render_template('enseignant/emploi_du_temps.html', 
                         emploi_du_temps=emploi_du_temps)

# Routes pour les notifications
@bp.route('/notifications')
@login_required
@enseignant_required
def notifications():
    """Liste des notifications de l'enseignant"""
    service_notification = ServiceNotification()
    notifications = service_notification.get_user_notifications(current_user.id)
    return render_template('enseignant/notifications/liste.html', notifications=notifications)

@bp.route('/notifications/liste')
@login_required
@enseignant_required
def liste_notifications():
    """Liste des notifications de l'enseignant (alias)"""
    return redirect(url_for('enseignant.notifications'))

@bp.route('/notifications/<int:notification_id>/marquer-lue')
@login_required
@enseignant_required
def marquer_notification_lue(notification_id):
    """Marquer une notification comme lue"""
    success = ServiceNotification.marquer_lue(notification_id, current_user.id)
    if success:
        return jsonify({'success': True, 'message': 'Notification marquée comme lue'})
    else:
        return jsonify({'success': False, 'message': 'Erreur lors du marquage de la notification'})

@bp.route('/notifications/<int:notification_id>/supprimer')
@login_required
@enseignant_required
def supprimer_notification(notification_id):
    """Supprimer une notification"""
    success = ServiceNotification.supprimer_notification(notification_id, current_user.id)
    if success:
        return jsonify({'success': True, 'message': 'Notification supprimée avec succès'})
    else:
        return jsonify({'success': False, 'message': 'Erreur lors de la suppression de la notification'})

@bp.route('/profil')
@login_required
@enseignant_required
def profil():
    """Profil de l'enseignant connecté"""
    enseignant = current_user.enseignant
    if not enseignant:
        flash('Profil enseignant non trouvé', 'error')
        return redirect(url_for('enseignant.dashboard'))
    
    return render_template('enseignant/profil.html', enseignant=enseignant) 