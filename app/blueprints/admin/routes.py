"""
Routes d'administration pour Edusco
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.admin import bp
from app.utils.decorateurs import administrateur_requis, utilisateur_actif_requis
from app.services.academique import ServiceAcademique
from app.forms.academique import (
    FormulaireAnneeAcademique, FormulaireSemestre, FormulaireUniteEnseignement,
    FormulaireMatiere, FormulaireEtudiant, FormulaireEnseignant, FormulaireGroupe
)
from app.models.academique import AnneeAcademique, Semestre, UniteEnseignement, Matiere, Etudiant, Enseignant, Groupe
from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.services.notification import ServiceNotification
from app.services.pedagogique import ServicePedagogique

@bp.route('/dashboard')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def dashboard():
    """Tableau de bord administrateur"""
    stats = ServiceAcademique.obtenir_statistiques_generales()
    annee_active = ServiceAcademique.obtenir_annee_active()
    
    # Récupérer les notifications récentes
    notifications = ServiceNotification.get_all_notifications()
    notifications_recentes = sorted(notifications, key=lambda x: x.date_creation, reverse=True)[:5]
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         annee_active=annee_active,
                         notifications=notifications_recentes)

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
    stats = ServiceAcademique.obtenir_statistiques_generales()
    return render_template('admin/statistiques.html', stats=stats)

# ==================== GESTION DES ANNÉES ACADÉMIQUES ====================

@bp.route('/annees-academiques')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def annees_academiques():
    """Liste des années académiques"""
    annees = ServiceAcademique.obtenir_toutes_annees()
    return render_template('admin/annees_academiques.html', annees=annees)

@bp.route('/annees-academiques/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_annee_academique():
    """Créer une nouvelle année académique"""
    formulaire = FormulaireAnneeAcademique()
    
    if formulaire.validate_on_submit():
        annee, succes = ServiceAcademique.creer_annee_academique(
            nom=formulaire.nom.data,
            date_debut=formulaire.date_debut.data,
            date_fin=formulaire.date_fin.data,
            active=formulaire.active.data
        )
        
        if succes:
            flash(f'Année académique "{annee.nom}" créée avec succès !', 'success')
            return redirect(url_for('admin.annees_academiques'))
        else:
            flash('Erreur lors de la création de l\'année académique.', 'error')
    
    return render_template('admin/creer_annee_academique.html', formulaire=formulaire)

@bp.route('/annees-academiques/<int:annee_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_annee_academique(annee_id):
    """Modifier une année académique"""
    annee = AnneeAcademique.query.get_or_404(annee_id)
    formulaire = FormulaireAnneeAcademique(obj=annee)
    
    if formulaire.validate_on_submit():
        succes = ServiceAcademique.modifier_annee_academique(
            annee_id=annee_id,
            nom=formulaire.nom.data,
            date_debut=formulaire.date_debut.data,
            date_fin=formulaire.date_fin.data,
            active=formulaire.active.data
        )
        
        if succes:
            flash(f'Année académique "{formulaire.nom.data}" modifiée avec succès !', 'success')
            return redirect(url_for('admin.annees_academiques'))
        else:
            flash('Erreur lors de la modification de l\'année académique.', 'error')
    
    return render_template('admin/modifier_annee_academique.html', formulaire=formulaire, annee=annee)

# ==================== GESTION DES SEMESTRES ====================

@bp.route('/semestres')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def semestres():
    """Liste des semestres"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active. Veuillez créer une année académique.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    semestres = ServiceAcademique.obtenir_semestres_par_annee(annee_active.id)
    return render_template('admin/semestres.html', semestres=semestres, annee_active=annee_active)

@bp.route('/semestres/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_semestre():
    """Créer un nouveau semestre"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active. Veuillez créer une année académique.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    formulaire = FormulaireSemestre()
    
    if formulaire.validate_on_submit():
        semestre, succes = ServiceAcademique.creer_semestre(
            nom=formulaire.nom.data,
            code=formulaire.code.data,
            date_debut=formulaire.date_debut.data,
            date_fin=formulaire.date_fin.data,
            annee_id=annee_active.id,
            actif=formulaire.actif.data
        )
        
        if succes:
            flash(f'Semestre "{semestre.nom}" créé avec succès !', 'success')
            return redirect(url_for('admin.semestres'))
        else:
            flash('Erreur lors de la création du semestre.', 'error')
    
    return render_template('admin/creer_semestre.html', formulaire=formulaire, annee_active=annee_active)

# ==================== GESTION DES UNITÉS D'ENSEIGNEMENT ====================

@bp.route('/unites-enseignement')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def unites_enseignement():
    """Liste des unités d'enseignement"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    semestres = ServiceAcademique.obtenir_semestres_par_annee(annee_active.id)
    return render_template('admin/unites_enseignement.html', semestres=semestres, annee_active=annee_active)

@bp.route('/unites-enseignement/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_unite_enseignement():
    """Créer une nouvelle unité d'enseignement"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    formulaire = FormulaireUniteEnseignement()
    
    # Remplir les choix de semestres
    semestres = ServiceAcademique.obtenir_semestres_par_annee(annee_active.id)
    formulaire.semestre_id.choices = [(s.id, f"{s.nom} - {s.code}") for s in semestres]
    
    if formulaire.validate_on_submit():
        ue, succes = ServiceAcademique.creer_unite_enseignement(
            code=formulaire.code.data,
            nom=formulaire.nom.data,
            description=formulaire.description.data,
            credits=formulaire.credits.data,
            coefficient=formulaire.coefficient.data,
            semestre_id=formulaire.semestre_id.data
        )
        
        if succes:
            flash(f'Unité d\'enseignement "{ue.code}" créée avec succès !', 'success')
            return redirect(url_for('admin.unites_enseignement'))
        else:
            flash('Erreur lors de la création de l\'unité d\'enseignement.', 'error')
    
    return render_template('admin/creer_unite_enseignement.html', formulaire=formulaire, annee_active=annee_active)

# ==================== GESTION DES MATIÈRES ====================

@bp.route('/matieres')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def matieres():
    """Liste des matières"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    semestres = ServiceAcademique.obtenir_semestres_par_annee(annee_active.id)
    return render_template('admin/matieres.html', semestres=semestres, annee_active=annee_active)

@bp.route('/matieres/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_matiere():
    """Créer une nouvelle matière"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    formulaire = FormulaireMatiere()
    
    # Remplir les choix d'enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    formulaire.enseignant_id.choices = [('', '-- Sélectionner un enseignant --')] + [(e.id, f"{e.nom_complet} ({e.matricule})") for e in enseignants]
    
    if formulaire.validate_on_submit():
        matiere, succes = ServiceAcademique.creer_matiere(
            code=formulaire.code.data,
            nom=formulaire.nom.data,
            description=formulaire.description.data,
            volume_horaire=formulaire.volume_horaire.data,
            coefficient=formulaire.coefficient.data,
            ue_id=formulaire.unite_enseignement_id.data,
            enseignant_id=formulaire.enseignant_id.data if formulaire.enseignant_id.data else None
        )
        
        if succes:
            flash(f'Matière "{matiere.code}" créée avec succès !', 'success')
            return redirect(url_for('admin.matieres'))
        else:
            flash('Erreur lors de la création de la matière.', 'error')
    
    return render_template('admin/creer_matiere.html', formulaire=formulaire, annee_active=annee_active)

# ==================== GESTION DES ÉTUDIANTS ====================

@bp.route('/etudiants')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def etudiants():
    """Liste des étudiants"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    etudiants = ServiceAcademique.obtenir_etudiants_par_annee(annee_active.id)
    return render_template('admin/etudiants.html', etudiants=etudiants, annee_active=annee_active)

@bp.route('/etudiants/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_etudiant():
    """Créer un nouvel étudiant"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    formulaire = FormulaireEtudiant()
    
    if formulaire.validate_on_submit():
        etudiant, succes = ServiceAcademique.creer_etudiant(
            matricule=formulaire.matricule.data,
            nom=formulaire.nom.data,
            prenom=formulaire.prenom.data,
            date_naissance=formulaire.date_naissance.data,
            sexe=formulaire.sexe.data,
            lieu_naissance=formulaire.lieu_naissance.data,
            adresse=formulaire.adresse.data,
            telephone=formulaire.telephone.data,
            email=formulaire.email.data,
            annee_id=annee_active.id
        )
        
        if succes:
            flash(f'Étudiant "{etudiant.nom_complet}" créé avec succès !', 'success')
            return redirect(url_for('admin.etudiants'))
        else:
            flash('Erreur lors de la création de l\'étudiant.', 'error')
    
    return render_template('admin/creer_etudiant.html', formulaire=formulaire, annee_active=annee_active)

@bp.route('/etudiants/rechercher')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def rechercher_etudiants():
    """Rechercher des étudiants"""
    terme = request.args.get('q', '')
    if terme:
        etudiants = ServiceAcademique.rechercher_etudiants(terme)
    else:
        annee_active = ServiceAcademique.obtenir_annee_active()
        etudiants = ServiceAcademique.obtenir_etudiants_par_annee(annee_active.id) if annee_active else []
    
    return render_template('admin/rechercher_etudiants.html', etudiants=etudiants, terme=terme)

# ==================== GESTION DES ENSEIGNANTS ====================

@bp.route('/enseignants')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def enseignants():
    """Liste des enseignants"""
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    return render_template('admin/enseignants.html', enseignants=enseignants)

@bp.route('/enseignants/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_enseignant():
    """Créer un nouvel enseignant"""
    formulaire = FormulaireEnseignant()
    
    if formulaire.validate_on_submit():
        enseignant, succes = ServiceAcademique.creer_enseignant(
            matricule=formulaire.matricule.data,
            nom=formulaire.nom.data,
            prenom=formulaire.prenom.data,
            date_naissance=formulaire.date_naissance.data,
            sexe=formulaire.sexe.data,
            date_embauche=formulaire.date_embauche.data,
            lieu_naissance=formulaire.lieu_naissance.data,
            adresse=formulaire.adresse.data,
            telephone=formulaire.telephone.data,
            email=formulaire.email.data,
            specialite=formulaire.specialite.data,
            grade=formulaire.grade.data
        )
        
        if succes:
            flash(f'Enseignant "{enseignant.nom_complet}" créé avec succès !', 'success')
            return redirect(url_for('admin.enseignants'))
        else:
            flash('Erreur lors de la création de l\'enseignant.', 'error')
    
    return render_template('admin/creer_enseignant.html', formulaire=formulaire)

# ==================== GESTION DES GROUPES ====================

@bp.route('/groupes')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def groupes():
    """Liste des groupes"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    semestres = ServiceAcademique.obtenir_semestres_par_annee(annee_active.id)
    return render_template('admin/groupes.html', semestres=semestres, annee_active=annee_active)

@bp.route('/groupes/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_groupe():
    """Créer un nouveau groupe"""
    annee_active = ServiceAcademique.obtenir_annee_active()
    if not annee_active:
        flash('Aucune année académique active.', 'warning')
        return redirect(url_for('admin.annees_academiques'))
    
    formulaire = FormulaireGroupe()
    
    # Remplir les choix d'enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    formulaire.enseignant_responsable_id.choices = [('', '-- Sélectionner un enseignant --')] + [(e.id, f"{e.nom_complet} ({e.matricule})") for e in enseignants]
    
    if formulaire.validate_on_submit():
        groupe, succes = ServiceAcademique.creer_groupe(
            nom=formulaire.nom.data,
            code=formulaire.code.data,
            capacite_max=formulaire.capacite_max.data,
            ue_id=formulaire.unite_enseignement_id.data,
            enseignant_id=formulaire.enseignant_responsable_id.data if formulaire.enseignant_responsable_id.data else None,
            description=formulaire.description.data
        )
        
        if succes:
            flash(f'Groupe "{groupe.code}" créé avec succès !', 'success')
            return redirect(url_for('admin.groupes'))
        else:
            flash('Erreur lors de la création du groupe.', 'error')
    
    return render_template('admin/creer_groupe.html', formulaire=formulaire, annee_active=annee_active)

# ==================== API ENDPOINTS ====================

@bp.route('/api/ues-par-semestre/<int:semestre_id>')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def api_ues_par_semestre(semestre_id):
    """API pour obtenir les UEs d'un semestre"""
    ues = ServiceAcademique.obtenir_ues_par_semestre(semestre_id)
    return jsonify([{'id': ue.id, 'code': ue.code, 'nom': ue.nom} for ue in ues])

@bp.route('/api/matieres-par-ue/<int:ue_id>')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def api_matieres_par_ue(ue_id):
    """API pour obtenir les matières d'une UE"""
    matieres = ServiceAcademique.obtenir_matieres_par_ue(ue_id)
    return jsonify([{'id': m.id, 'code': m.code, 'nom': m.nom} for m in matieres])

@bp.route('/api/groupes-par-ue/<int:ue_id>')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def api_groupes_par_ue(ue_id):
    """API pour obtenir les groupes d'une UE"""
    groupes = ServiceAcademique.obtenir_groupes_par_ue(ue_id)
    return jsonify([{'id': g.id, 'code': g.code, 'nom': g.nom} for g in groupes])

# ==================== GESTION PÉDAGOGIQUE ====================

@bp.route('/pedagogique')
@login_required
@administrateur_requis
def pedagogique_dashboard():
    """Tableau de bord pédagogique"""
    # Statistiques globales
    total_notes = Note.query.count()
    total_absences = Absence.query.count()
    total_deliberations = Deliberation.query.count()
    
    # Délibérations en cours
    deliberations_en_cours = Deliberation.query.filter_by(statut=Deliberation.STATUT_EN_COURS).count()
    
    return render_template('admin/pedagogique/dashboard.html',
                         total_notes=total_notes,
                         total_absences=total_absences,
                         total_deliberations=total_deliberations,
                         deliberations_en_cours=deliberations_en_cours)

# ==================== VALIDATION DES NOTES ====================

@bp.route('/pedagogique/notes')
@login_required
@administrateur_requis
def validation_notes():
    """Validation des notes saisies par les enseignants"""
    # Filtres
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    enseignant_id = request.args.get('enseignant_id', type=int)
    
    query = Note.query
    
    if matiere_id:
        query = query.filter(Note.matiere_id == matiere_id)
    if groupe_id:
        query = query.filter(Note.groupe_id == groupe_id)
    if enseignant_id:
        query = query.filter(Note.enseignant_id == enseignant_id)
    
    notes = query.order_by(Note.date_saisie.desc()).all()
    
    # Données pour les filtres
    matieres = Matiere.query.all()
    groupes = Groupe.query.all()
    enseignants = Enseignant.query.all()
    
    return render_template('admin/pedagogique/validation_notes.html',
                         notes=notes,
                         matieres=matieres,
                         groupes=groupes,
                         enseignants=enseignants,
                         matiere_selectionnee=matiere_id,
                         groupe_selectionne=groupe_id,
                         enseignant_selectionne=enseignant_id)

@bp.route('/pedagogique/notes/<int:note_id>/valider', methods=['POST'])
@login_required
@administrateur_requis
def valider_note(note_id):
    """Valider une note"""
    note = Note.query.get(note_id)
    if not note:
        flash('Note non trouvée', 'error')
        return redirect(url_for('admin.validation_notes'))
    
    # Logique de validation (à implémenter selon les besoins)
    # Par exemple, marquer la note comme validée par l'admin
    
    flash('Note validée avec succès', 'success')
    return redirect(url_for('admin.validation_notes'))

# ==================== GESTION DES DÉLIBÉRATIONS ====================

@bp.route('/pedagogique/deliberations')
@login_required
@administrateur_requis
def deliberations():
    """Liste des délibérations"""
    deliberations = Deliberation.query.order_by(Deliberation.date_deliberation.desc()).all()
    return render_template('admin/pedagogique/deliberations.html', deliberations=deliberations)

@bp.route('/pedagogique/deliberations/creer', methods=['GET', 'POST'])
@login_required
@administrateur_requis
def creer_deliberation():
    """Créer une nouvelle délibération"""
    if request.method == 'POST':
        semestre_id = request.form.get('semestre_id', type=int)
        groupe_id = request.form.get('groupe_id', type=int)
        commentaire = request.form.get('commentaire', '')
        
        deliberation, succes = ServicePedagogique.creer_deliberation(
            semestre_id=semestre_id,
            groupe_id=groupe_id,
            commentaire=commentaire
        )
        
        if succes:
            flash('Délibération créée avec succès', 'success')
            return redirect(url_for('admin.deliberations'))
        else:
            flash('Erreur lors de la création de la délibération', 'error')
    
    # Données pour le formulaire
    semestres = Semestre.query.all()
    groupes = Groupe.query.all()
    
    return render_template('admin/pedagogique/creer_deliberation.html',
                         semestres=semestres,
                         groupes=groupes)

@bp.route('/pedagogique/deliberations/<int:deliberation_id>')
@login_required
@administrateur_requis
def detail_deliberation(deliberation_id):
    """Détail d'une délibération"""
    deliberation = Deliberation.query.get(deliberation_id)
    if not deliberation:
        flash('Délibération non trouvée', 'error')
        return redirect(url_for('admin.deliberations'))
    
    return render_template('admin/pedagogique/detail_deliberation.html', deliberation=deliberation)

@bp.route('/pedagogique/deliberations/<int:deliberation_id>/calculer', methods=['POST'])
@login_required
@administrateur_requis
def calculer_deliberation(deliberation_id):
    """Calculer les résultats de délibération"""
    succes = ServicePedagogique.calculer_resultats_deliberation(deliberation_id)
    
    if succes:
        flash('Résultats calculés avec succès', 'success')
    else:
        flash('Erreur lors du calcul des résultats', 'error')
    
    return redirect(url_for('admin.detail_deliberation', deliberation_id=deliberation_id))

@bp.route('/pedagogique/deliberations/<int:deliberation_id>/valider', methods=['POST'])
@login_required
@administrateur_requis
def valider_deliberation(deliberation_id):
    """Valider une délibération"""
    commentaire = request.form.get('commentaire', '')
    succes = ServicePedagogique.valider_deliberation(deliberation_id, commentaire)
    
    if succes:
        flash('Délibération validée avec succès', 'success')
    else:
        flash('Erreur lors de la validation', 'error')
    
    return redirect(url_for('admin.detail_deliberation', deliberation_id=deliberation_id))

# ==================== GESTION DES EMPLOIS DU TEMPS ====================

@bp.route('/pedagogique/emplois-du-temps')
@login_required
@administrateur_requis
def emplois_du_temps():
    """Gestion des emplois du temps"""
    # Filtres
    groupe_id = request.args.get('groupe_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    
    query = EmploiDuTemps.query.filter_by(actif=True)
    
    if groupe_id:
        query = query.filter(EmploiDuTemps.groupe_id == groupe_id)
    if semestre_id:
        query = query.filter(EmploiDuTemps.semestre_id == semestre_id)
    
    emplois_du_temps = query.order_by(EmploiDuTemps.jour, EmploiDuTemps.heure_debut).all()
    
    # Données pour les filtres
    groupes = Groupe.query.all()
    semestres = Semestre.query.all()
    
    return render_template('admin/pedagogique/emplois_du_temps.html',
                         emplois_du_temps=emplois_du_temps,
                         groupes=groupes,
                         semestres=semestres,
                         groupe_selectionne=groupe_id,
                         semestre_selectionne=semestre_id)

@bp.route('/pedagogique/emplois-du-temps/creer', methods=['GET', 'POST'])
@login_required
@administrateur_requis
def creer_emploi_du_temps():
    """Créer un emploi du temps"""
    if request.method == 'POST':
        groupe_id = request.form.get('groupe_id', type=int)
        matiere_id = request.form.get('matiere_id', type=int)
        enseignant_id = request.form.get('enseignant_id', type=int)
        semestre_id = request.form.get('semestre_id', type=int)
        jour = request.form.get('jour', type=int)
        heure_debut = datetime.strptime(request.form.get('heure_debut'), '%H:%M').time()
        heure_fin = datetime.strptime(request.form.get('heure_fin'), '%H:%M').time()
        salle = request.form.get('salle', '')
        
        edt, succes = ServicePedagogique.creer_emploi_du_temps(
            groupe_id=groupe_id,
            matiere_id=matiere_id,
            enseignant_id=enseignant_id,
            semestre_id=semestre_id,
            jour=jour,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            salle=salle
        )
        
        if succes:
            flash('Emploi du temps créé avec succès', 'success')
            return redirect(url_for('admin.emplois_du_temps'))
        else:
            flash('Erreur lors de la création (conflit possible)', 'error')
    
    # Données pour le formulaire
    groupes = Groupe.query.all()
    matieres = Matiere.query.all()
    enseignants = Enseignant.query.all()
    semestres = Semestre.query.all()
    
    return render_template('admin/pedagogique/creer_emploi_du_temps.html',
                         groupes=groupes,
                         matieres=matieres,
                         enseignants=enseignants,
                         semestres=semestres)

# ==================== RAPPORTS ET STATISTIQUES ====================

@bp.route('/pedagogique/rapports')
@login_required
@administrateur_requis
def rapports_pedagogiques():
    """Rapports pédagogiques globaux"""
    # Statistiques globales
    total_etudiants = Etudiant.query.count()
    total_enseignants = Enseignant.query.count()
    total_notes = Note.query.count()
    total_absences = Absence.query.count()
    
    # Moyenne générale (exemple)
    moyenne_generale = 0
    if total_notes > 0:
        result = db.session.query(func.avg(Note.note)).scalar()
        moyenne_generale = result if result else 0
    
    return render_template('admin/pedagogique/rapports.html',
                         total_etudiants=total_etudiants,
                         total_enseignants=total_enseignants,
                         total_notes=total_notes,
                         total_absences=total_absences,
                         moyenne_generale=moyenne_generale)

@bp.route('/pedagogique/rapports/etudiant/<int:etudiant_id>')
@login_required
@administrateur_requis
def rapport_etudiant(etudiant_id):
    """Rapport détaillé d'un étudiant"""
    etudiant = Etudiant.query.get(etudiant_id)
    if not etudiant:
        flash('Étudiant non trouvé', 'error')
        return redirect(url_for('admin.rapports_pedagogiques'))
    
    # Notes de l'étudiant
    notes = ServicePedagogique.obtenir_notes_etudiant(etudiant_id)
    
    # Absences de l'étudiant
    absences = ServicePedagogique.obtenir_absences_etudiant(etudiant_id)
    
    # Résultats de délibération
    resultats = ServicePedagogique.obtenir_resultats_etudiant(etudiant_id)
    
    return render_template('admin/pedagogique/rapport_etudiant.html',
                         etudiant=etudiant,
                         notes=notes,
                         absences=absences,
                         resultats=resultats)

# Routes pour les notifications
@bp.route('/notifications')
@login_required
@administrateur_requis
def notifications():
    """Afficher la liste des notifications"""
    notifications = ServiceNotification.get_all_notifications()
    return render_template('admin/notifications/liste.html', notifications=notifications)

@bp.route('/notifications/<int:notification_id>/marquer-lue')
@login_required
@administrateur_requis
def marquer_notification_lue(notification_id):
    """Marquer une notification comme lue"""
    success = ServiceNotification.marquer_lue(notification_id)
    if success:
        flash('Notification marquée comme lue', 'success')
    else:
        flash('Erreur lors du marquage de la notification', 'error')
    return redirect(url_for('admin.notifications'))

@bp.route('/notifications/<int:notification_id>/supprimer')
@login_required
@administrateur_requis
def supprimer_notification(notification_id):
    """Supprimer une notification"""
    success = ServiceNotification.supprimer_notification(notification_id)
    if success:
        flash('Notification supprimée avec succès', 'success')
    else:
        flash('Erreur lors de la suppression de la notification', 'error')
    return redirect(url_for('admin.notifications'))

@bp.route('/notifications/envoyer', methods=['GET', 'POST'])
@login_required
@administrateur_requis
def envoyer_notification():
    """Envoyer une notification à un utilisateur ou groupe d'utilisateurs"""
    if request.method == 'POST':
        destinataire_type = request.form.get('destinataire_type')
        destinataire_id = request.form.get('destinataire_id')
        titre = request.form.get('titre')
        message = request.form.get('message')
        envoyer_email = request.form.get('envoyer_email') == 'on'
        
        if destinataire_type == 'utilisateur':
            success = ServiceNotification.creer_notification(
                utilisateur_id=destinataire_id,
                titre=titre,
                message=message,
                envoyer_email=envoyer_email
            )
        elif destinataire_type == 'groupe':
            # Envoyer à tous les étudiants d'un groupe
            success = ServiceNotification.creer_notification_groupe(
                groupe_id=destinataire_id,
                titre=titre,
                message=message,
                envoyer_email=envoyer_email
            )
        else:
            # Envoyer à tous les utilisateurs
            success = ServiceNotification.creer_notification_globale(
                titre=titre,
                message=message,
                envoyer_email=envoyer_email
            )
        
        if success:
            flash('Notification envoyée avec succès', 'success')
        else:
            flash('Erreur lors de l\'envoi de la notification', 'error')
        
        return redirect(url_for('admin.notifications'))
    
    # Récupérer les listes pour le formulaire
    utilisateurs = Utilisateur.query.all()
    groupes = Groupe.query.all()
    
    return render_template('admin/notifications/envoyer.html', 
                         utilisateurs=utilisateurs, 
                         groupes=groupes) 