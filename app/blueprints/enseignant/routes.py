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
from app.utils.decorateurs import enseignant_requis
from app.extensions import db
from datetime import datetime, date, time
import json

bp = Blueprint('enseignant', __name__, url_prefix='/enseignant')

@bp.route('/dashboard')
@login_required
@enseignant_requis
def dashboard():
    """Tableau de bord de l'enseignant"""
    return render_template('enseignant/dashboard.html')

@bp.route('/')
def index():
    """Page d'accueil enseignant"""
    return redirect(url_for('enseignant.dashboard'))

@bp.route('/notes')
@login_required
@enseignant_requis
def notes():
    """Liste des notes saisies par l'enseignant"""
    enseignant = current_user.enseignant
    matieres = ServiceAcademique.obtenir_matieres_enseignant(enseignant.id)
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    notes = []
    if matiere_id:
        matiere = Matiere.query.get(matiere_id)
        if matiere and matiere.enseignant_id == enseignant.id:
            notes = Note.query.filter_by(matiere_id=matiere_id).order_by(Note.date_evaluation.desc()).all()
    return render_template('enseignant/notes.html', notes=notes, matieres=matieres, matiere_selectionnee=matiere_id)

@bp.route('/notes/saisir/<int:groupe_id>/<int:matiere_id>', methods=['GET', 'POST'])
@login_required
@enseignant_requis
def saisir_notes(groupe_id, matiere_id):
    """Saisie ou modification des notes pour un groupe et une matière"""
    enseignant = current_user.enseignant
    matiere = Matiere.query.get(matiere_id)
    if not matiere or matiere.enseignant_id != enseignant.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('enseignant.notes'))
    etudiants = ServiceAcademique.obtenir_etudiants_groupe(groupe_id)
    type_evaluation = request.args.get('type', 'controle')
    date_evaluation = request.args.get('date', date.today().isoformat())
    notes_existantes = {}
    if date_evaluation:
        try:
            date_eval = datetime.strptime(date_evaluation, '%Y-%m-%d').date()
            notes = Note.query.filter(
                Note.matiere_id == matiere_id,
                Note.groupe_id == groupe_id,
                Note.date_evaluation == date_eval,
                Note.type_evaluation == type_evaluation
            ).all()
            for note in notes:
                notes_existantes[note.etudiant_id] = note
        except ValueError:
            pass
    if request.method == 'POST':
        for etudiant in etudiants:
            note_value = request.form.get(f'note_{etudiant.id}')
            commentaire = request.form.get(f'commentaire_{etudiant.id}', '')
            if note_value is not None and note_value != '':
                note_value = float(note_value)
                note_existante = Note.query.filter(
                    Note.etudiant_id == etudiant.id,
                    Note.matiere_id == matiere_id,
                    Note.groupe_id == groupe_id,
                    Note.date_evaluation == date_eval,
                    Note.type_evaluation == type_evaluation
                ).first()
                if note_existante:
                    note_existante.note = note_value
                    note_existante.commentaire = commentaire
                else:
                    ServicePedagogique.creer_note(
                        etudiant_id=etudiant.id,
                        matiere_id=matiere_id,
                        groupe_id=groupe_id,
                        enseignant_id=enseignant.id,
                        type_evaluation=type_evaluation,
                        note=note_value,
                        commentaire=commentaire,
                        date_evaluation=date_eval
                    )
        db.session.commit()
        flash('Notes enregistrées avec succès', 'success')
        return redirect(url_for('enseignant.notes'))
    return render_template('enseignant/saisir_notes.html', matiere=matiere, groupe_id=groupe_id, etudiants=etudiants, notes_existantes=notes_existantes, type_evaluation=type_evaluation, date_evaluation=date_evaluation)

@bp.route('/notes/modifier/<int:note_id>', methods=['GET', 'POST'])
@login_required
@enseignant_requis
def modifier_note(note_id):
    enseignant = current_user.enseignant
    note = Note.query.get(note_id)
    if not note or note.enseignant_id != enseignant.id:
        flash('Note non trouvée ou accès non autorisé', 'error')
        return redirect(url_for('enseignant.notes'))
    if request.method == 'POST':
        try:
            note_value = float(request.form.get('note'))
            commentaire = request.form.get('commentaire', '')
            note.note = note_value
            note.commentaire = commentaire
            db.session.commit()
            flash('Note modifiée avec succès', 'success')
            return redirect(url_for('enseignant.notes'))
        except ValueError:
            flash('Valeur de note invalide', 'error')
    return render_template('enseignant/modifier_note.html', note=note)

@bp.route('/notes/supprimer/<int:note_id>', methods=['POST'])
@login_required
@enseignant_requis
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

@bp.route('/rapports/notes/<int:groupe_id>/<int:matiere_id>')
@login_required
@enseignant_requis
def rapport_notes(groupe_id, matiere_id):
    enseignant = current_user.enseignant
    matiere = Matiere.query.get(matiere_id)
    if not matiere or matiere.enseignant_id != enseignant.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('enseignant.dashboard'))
    etudiants = ServiceAcademique.obtenir_etudiants_groupe(groupe_id)
    moyennes = {etudiant.id: ServicePedagogique.calculer_moyenne_etudiant(etudiant.id, matiere_id) for etudiant in etudiants}
    moyennes_list = list(moyennes.values())
    moyenne_classe = sum(moyennes_list) / len(moyennes_list) if moyennes_list else 0
    note_max = max(moyennes_list) if moyennes_list else 0
    note_min = min(moyennes_list) if moyennes_list else 0
    return render_template('enseignant/rapport_notes.html', matiere=matiere, groupe_id=groupe_id, etudiants=etudiants, moyennes=moyennes, moyenne_classe=moyenne_classe, note_max=note_max, note_min=note_min)

@bp.route('/absences')
@login_required
@enseignant_requis
def absences():
    enseignant = current_user.enseignant
    groupe_id = request.args.get('groupe_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    absences = []
    if groupe_id:
        groupe = Groupe.query.get(groupe_id)
        if groupe and groupe.enseignant_id == enseignant.id:
            query = Absence.query.filter_by(groupe_id=groupe_id)
            if date_debut:
                try:
                    debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
                    query = query.filter(Absence.date_absence >= debut)
                except ValueError:
                    pass
            if date_fin:
                try:
                    fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
                    query = query.filter(Absence.date_absence <= fin)
                except ValueError:
                    pass
            absences = query.order_by(Absence.date_absence.desc()).all()
    groupes = ServiceAcademique.obtenir_groupes_enseignant(enseignant.id)
    return render_template('enseignant/absences.html', absences=absences, groupes=groupes, groupe_selectionne=groupe_id)

@bp.route('/absences/saisir/<int:groupe_id>', methods=['GET', 'POST'])
@login_required
@enseignant_requis
def saisir_absences(groupe_id):
    enseignant = current_user.enseignant
    groupe = Groupe.query.get(groupe_id)
    if not groupe or groupe.enseignant_id != enseignant.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('enseignant.absences'))
    etudiants = ServiceAcademique.obtenir_etudiants_groupe(groupe_id)
    matieres = ServiceAcademique.obtenir_matieres_enseignant(enseignant.id)
    if request.method == 'POST':
        matiere_id = request.form.get('matiere_id', type=int)
        date_absence = request.form.get('date_absence')
        heure_debut = request.form.get('heure_debut')
        heure_fin = request.form.get('heure_fin')
        motif = request.form.get('motif', '')
        for etudiant in etudiants:
            absent = request.form.get(f'absent_{etudiant.id}')
            justifiee = request.form.get(f'justifiee_{etudiant.id}') == 'on'
            commentaire = request.form.get(f'commentaire_{etudiant.id}', '')
            if absent:
                ServicePedagogique.creer_absence(
                    etudiant_id=etudiant.id,
                    matiere_id=matiere_id,
                    groupe_id=groupe_id,
                    date_absence=datetime.strptime(date_absence, '%Y-%m-%d').date(),
                    heure_debut=datetime.strptime(heure_debut, '%H:%M').time(),
                    heure_fin=datetime.strptime(heure_fin, '%H:%M').time(),
                    motif=motif,
                    justifiee=justifiee,
                    commentaire=commentaire
                )
        db.session.commit()
        flash('Absences enregistrées avec succès', 'success')
        return redirect(url_for('enseignant.absences'))
    return render_template('enseignant/saisir_absences.html', groupe=groupe, etudiants=etudiants, matieres=matieres)

@bp.route('/absences/modifier/<int:absence_id>', methods=['GET', 'POST'])
@login_required
@enseignant_requis
def modifier_absence(absence_id):
    enseignant = current_user.enseignant
    absence = Absence.query.get(absence_id)
    if not absence:
        flash('Absence non trouvée', 'error')
        return redirect(url_for('enseignant.absences'))
    groupe = Groupe.query.get(absence.groupe_id)
    if not groupe or groupe.enseignant_id != enseignant.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('enseignant.absences'))
    if request.method == 'POST':
        justifiee = request.form.get('justifiee') == 'on'
        motif = request.form.get('motif', '')
        commentaire = request.form.get('commentaire', '')
        absence.justifiee = justifiee
        absence.motif = motif
        absence.commentaire = commentaire
        db.session.commit()
        flash('Absence modifiée avec succès', 'success')
        return redirect(url_for('enseignant.absences'))
    return render_template('enseignant/modifier_absence.html', absence=absence)

@bp.route('/absences/supprimer/<int:absence_id>', methods=['POST'])
@login_required
@enseignant_requis
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

@bp.route('/rapports/absences/<int:groupe_id>')
@login_required
@enseignant_requis
def rapport_absences(groupe_id):
    enseignant = current_user.enseignant
    groupe = Groupe.query.get(groupe_id)
    if not groupe or groupe.enseignant_id != enseignant.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('enseignant.dashboard'))
    etudiants = ServiceAcademique.obtenir_etudiants_groupe(groupe_id)
    taux_absences = {etudiant.id: ServicePedagogique.calculer_taux_absence_etudiant(etudiant.id) for etudiant in etudiants}
    return render_template('enseignant/rapport_absences.html', groupe=groupe, etudiants=etudiants, taux_absences=taux_absences)

@bp.route('/emploi-du-temps')
@login_required
@enseignant_requis
def emploi_du_temps():
    """Emploi du temps de l'enseignant"""
    return render_template('enseignant/emploi_du_temps.html') 