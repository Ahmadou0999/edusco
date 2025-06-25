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

@bp.route('/dashboard')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def dashboard():
    """Tableau de bord administrateur"""
    stats = ServiceAcademique.obtenir_statistiques_generales()
    annee_active = ServiceAcademique.obtenir_annee_active()
    return render_template('admin/dashboard.html', stats=stats, annee_active=annee_active)

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