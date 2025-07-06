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
from datetime import datetime, date
from sqlalchemy.sql import func
from app.services.notification import ServiceNotification
from app.services.pedagogique import ServicePedagogique
from app.models.utilisateur import Utilisateur

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
def utilisateurs():
    """Liste paginée des utilisateurs"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    from app.services.authentification import ServiceAuthentification
    service_auth = ServiceAuthentification()
    
    # Récupérer tous les utilisateurs et filtrer côté Python pour la recherche
    utilisateurs = service_auth.get_tous_utilisateurs()
    
    # Filtrage côté Python
    if search:
        utilisateurs = [u for u in utilisateurs if 
                       search.lower() in u.nom.lower() or 
                       search.lower() in u.prenom.lower() or 
                       search.lower() in u.email.lower() or
                       (u.enseignant and search.lower() in u.enseignant.matricule.lower()) or
                       (u.etudiant and search.lower() in u.etudiant.matricule.lower())]
    
    # Pagination manuelle
    total = len(utilisateurs)
    start = (page - 1) * per_page
    end = start + per_page
    utilisateurs_pagines = utilisateurs[start:end]
    
    # Créer un objet paginé simulé
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < self.pages else None
            
        def iter_pages(self):
            return range(1, self.pages + 1)
    
    pagination = Pagination(utilisateurs_pagines, page, per_page, total)
    
    return render_template('admin/utilisateurs.html', utilisateurs=pagination, search=search)

@bp.route('/utilisateurs/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_utilisateurs():
    """Exporter les utilisateurs en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    from app.services.authentification import ServiceAuthentification
    
    service_auth = ServiceAuthentification()
    utilisateurs = service_auth.get_tous_utilisateurs()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Nom', 'Prénom', 'Email', 'Rôle', 'Statut', 'Date création', 'Dernière connexion', 'Matricule académique'])
    
    for utilisateur in utilisateurs:
        matricule = ''
        if utilisateur.enseignant:
            matricule = utilisateur.enseignant.matricule
        elif utilisateur.etudiant:
            matricule = utilisateur.etudiant.matricule
            
        writer.writerow([
            utilisateur.nom,
            utilisateur.prenom,
            utilisateur.email,
            utilisateur.role,
            'Actif' if utilisateur.actif else 'Inactif',
            utilisateur.date_creation.strftime('%d/%m/%Y %H:%M') if utilisateur.date_creation else '',
            utilisateur.derniere_connexion.strftime('%d/%m/%Y %H:%M') if utilisateur.derniere_connexion else 'Jamais',
            matricule
        ])
    
    output.seek(0)
    filename = f"utilisateurs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/creer-utilisateur', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_utilisateur():
    """Créer un nouvel utilisateur avec choix explicite du rôle"""
    from app.services.authentification import ServiceAuthentification
    from app.forms.authentification import GestionUtilisateurForm
    
    form = GestionUtilisateurForm()
    
    if form.validate_on_submit():
        service_auth = ServiceAuthentification()
        
        try:
            # Créer l'utilisateur avec le rôle choisi explicitement
            utilisateur, succes = service_auth.creer_utilisateur(
                nom=form.nom.data,
                prenom=form.prenom.data,
                email=form.email.data,
                mot_de_passe=form.mot_de_passe.data,
                role=form.role.data  # Rôle choisi explicitement par l'admin
            )
            
            if succes and utilisateur:
                # Activer le compte si demandé
                if form.actif.data:
                    utilisateur.actif = True
                    db.session.commit()
                
                flash(f'Utilisateur "{utilisateur.nom} {utilisateur.prenom}" créé avec succès avec le rôle "{form.role.data}"', 'success')
                return redirect(url_for('admin.utilisateurs'))
            else:
                flash('Erreur lors de la création de l\'utilisateur.', 'error')
            
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    return render_template('admin/creer_utilisateur.html', form=form)

@bp.route('/utilisateurs/<int:utilisateur_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_utilisateur(utilisateur_id):
    """Modifier un utilisateur existant"""
    from app.services.authentification import ServiceAuthentification
    from app.forms.authentification import GestionUtilisateurForm
    
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    form = GestionUtilisateurForm(obj=utilisateur, utilisateur_existant=utilisateur)
    ancien_role = utilisateur.role
    
    if form.validate_on_submit():
        try:
            utilisateur.nom = form.nom.data
            utilisateur.prenom = form.prenom.data
            utilisateur.email = form.email.data
            utilisateur.role = form.role.data
            utilisateur.actif = form.actif.data
            # Synchronisation des profils
            if ancien_role != utilisateur.role:
                if utilisateur.role == 'enseignant':
                    # Supprimer profil étudiant si existant
                    if utilisateur.etudiant:
                        db.session.delete(utilisateur.etudiant)
                elif utilisateur.role == 'etudiant':
                    # Supprimer profil enseignant si existant
                    if utilisateur.enseignant:
                        db.session.delete(utilisateur.enseignant)
                else:
                    # Supprimer tous les profils si le rôle n'est ni enseignant ni étudiant
                    if utilisateur.enseignant:
                        db.session.delete(utilisateur.enseignant)
                    if utilisateur.etudiant:
                        db.session.delete(utilisateur.etudiant)
            db.session.commit()
            flash(f'Utilisateur "{utilisateur.nom} {utilisateur.prenom}" modifié avec succès', 'success')
            return redirect(url_for('admin.utilisateurs'))
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    return render_template('admin/modifier_utilisateur.html', form=form, utilisateur=utilisateur)

@bp.route('/utilisateurs/<int:utilisateur_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_utilisateur(utilisateur_id):
    """Supprimer un utilisateur"""
    try:
        utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
        # Empêcher la suppression de l'utilisateur connecté
        if utilisateur.id == current_user.id:
            flash('Vous ne pouvez pas supprimer votre propre compte', 'error')
            return redirect(url_for('admin.utilisateurs'))
        nom_utilisateur = f"{utilisateur.nom} {utilisateur.prenom}"
        # Suppression du profil académique lié
        if utilisateur.enseignant:
            db.session.delete(utilisateur.enseignant)
        if utilisateur.etudiant:
            db.session.delete(utilisateur.etudiant)
        db.session.delete(utilisateur)
        db.session.commit()
        flash(f'Utilisateur "{nom_utilisateur}" et son profil académique supprimés avec succès', 'success')
    except Exception as e:
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    return redirect(url_for('admin.utilisateurs'))

@bp.route('/utilisateurs/<int:utilisateur_id>/creer-profil-enseignant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_profil_enseignant(utilisateur_id):
    """Créer un profil enseignant pour un utilisateur existant"""
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    
    # Vérifier que l'utilisateur a le bon rôle
    if utilisateur.role != 'enseignant':
        flash('Seuls les utilisateurs avec le rôle "enseignant" peuvent avoir un profil enseignant.', 'error')
        return redirect(url_for('admin.utilisateurs'))
    
    # Vérifier qu'il n'a pas déjà un profil enseignant
    if utilisateur.enseignant:
        flash('Cet utilisateur a déjà un profil enseignant.', 'warning')
        return redirect(url_for('admin.utilisateurs'))
    
    try:
        # Récupérer les données du formulaire
        matricule = request.form.get('matricule')
        specialite = request.form.get('specialite', '')
        grade = request.form.get('grade', '')
        date_embauche = datetime.strptime(request.form.get('date_embauche'), '%Y-%m-%d').date()
        telephone = request.form.get('telephone', '')
        adresse = request.form.get('adresse', '')
        
        # Vérifier que le matricule n'existe pas déjà
        if Enseignant.query.filter_by(matricule=matricule).first():
            flash('Ce matricule existe déjà. Veuillez choisir un autre matricule.', 'error')
            return redirect(url_for('admin.utilisateurs'))
        
        # Créer le profil enseignant
        enseignant = Enseignant(
            matricule=matricule,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            date_naissance=datetime.now().date(),  # Valeur par défaut, à modifier plus tard
            sexe='M',  # Valeur par défaut, à modifier plus tard
            specialite=specialite,
            grade=grade,
            telephone=telephone,
            email=utilisateur.email,
            adresse=adresse,
            date_embauche=date_embauche,
            utilisateur_id=utilisateur.id
        )
        
        db.session.add(enseignant)
        db.session.commit()
        
        flash(f'Profil enseignant créé avec succès pour {utilisateur.prenom} {utilisateur.nom} (Matricule: {matricule})', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la création du profil enseignant: {str(e)}', 'error')
    
    return redirect(url_for('admin.utilisateurs'))

@bp.route('/utilisateurs/<int:utilisateur_id>/creer-profil-etudiant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_profil_etudiant(utilisateur_id):
    """Créer un profil étudiant pour un utilisateur existant"""
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    
    # Vérifier que l'utilisateur a le bon rôle
    if utilisateur.role != 'etudiant':
        flash('Seuls les utilisateurs avec le rôle "etudiant" peuvent avoir un profil étudiant.', 'error')
        return redirect(url_for('admin.utilisateurs'))
    
    # Vérifier qu'il n'a pas déjà un profil étudiant
    if utilisateur.etudiant:
        flash('Cet utilisateur a déjà un profil étudiant.', 'warning')
        return redirect(url_for('admin.utilisateurs'))
    
    try:
        # Récupérer les données du formulaire
        matricule = request.form.get('matricule')
        date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d').date()
        sexe = request.form.get('sexe')
        telephone = request.form.get('telephone', '')
        adresse = request.form.get('adresse', '')
        
        # Vérifier que le matricule n'existe pas déjà
        if Etudiant.query.filter_by(matricule=matricule).first():
            flash('Ce matricule existe déjà. Veuillez choisir un autre matricule.', 'error')
            return redirect(url_for('admin.utilisateurs'))
        
        # Obtenir l'année académique active
        annee_active = ServiceAcademique.obtenir_annee_active()
        if not annee_active:
            flash('Aucune année académique active. Veuillez d\'abord créer et activer une année académique.', 'error')
            return redirect(url_for('admin.utilisateurs'))
        
        # Créer le profil étudiant
        etudiant = Etudiant(
            matricule=matricule,
            nom=utilisateur.nom,
            prenom=utilisateur.prenom,
            date_naissance=date_naissance,
            sexe=sexe,
            telephone=telephone,
            email=utilisateur.email,
            adresse=adresse,
            annee_academique_id=annee_active.id,
            utilisateur_id=utilisateur.id
        )
        
        db.session.add(etudiant)
        db.session.commit()
        
        flash(f'Profil étudiant créé avec succès pour {utilisateur.prenom} {utilisateur.nom} (Matricule: {matricule})', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la création du profil étudiant: {str(e)}', 'error')
    
    return redirect(url_for('admin.utilisateurs'))

@bp.route('/utilisateurs/<int:utilisateur_id>/modifier-profil-enseignant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_profil_enseignant(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    enseignant = utilisateur.enseignant
    if not enseignant:
        flash('Aucun profil enseignant à modifier.', 'error')
        return redirect(url_for('admin.utilisateurs'))
    try:
        matricule = request.form.get('matricule')
        specialite = request.form.get('specialite', '')
        grade = request.form.get('grade', '')
        date_embauche = datetime.strptime(request.form.get('date_embauche'), '%Y-%m-%d').date()
        telephone = request.form.get('telephone', '')
        adresse = request.form.get('adresse', '')
        # Vérifier unicité du matricule
        autre = Enseignant.query.filter(Enseignant.matricule==matricule, Enseignant.id!=enseignant.id).first()
        if autre:
            flash('Ce matricule existe déjà pour un autre enseignant.', 'error')
            return redirect(url_for('admin.utilisateurs'))
        enseignant.matricule = matricule
        enseignant.specialite = specialite
        enseignant.grade = grade
        enseignant.date_embauche = date_embauche
        enseignant.telephone = telephone
        enseignant.adresse = adresse
        db.session.commit()
        flash('Profil enseignant modifié avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la modification du profil enseignant: {str(e)}', 'error')
    return redirect(url_for('admin.utilisateurs'))

@bp.route('/utilisateurs/<int:utilisateur_id>/modifier-profil-etudiant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_profil_etudiant(utilisateur_id):
    utilisateur = Utilisateur.query.get_or_404(utilisateur_id)
    etudiant = utilisateur.etudiant
    if not etudiant:
        flash('Aucun profil étudiant à modifier.', 'error')
        return redirect(url_for('admin.utilisateurs'))
    try:
        matricule = request.form.get('matricule')
        date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d').date()
        sexe = request.form.get('sexe')
        telephone = request.form.get('telephone', '')
        adresse = request.form.get('adresse', '')
        # Vérifier unicité du matricule
        autre = Etudiant.query.filter(Etudiant.matricule==matricule, Etudiant.id!=etudiant.id).first()
        if autre:
            flash('Ce matricule existe déjà pour un autre étudiant.', 'error')
            return redirect(url_for('admin.utilisateurs'))
        etudiant.matricule = matricule
        etudiant.date_naissance = date_naissance
        etudiant.sexe = sexe
        etudiant.telephone = telephone
        etudiant.adresse = adresse
        db.session.commit()
        flash('Profil étudiant modifié avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la modification du profil étudiant: {str(e)}', 'error')
    return redirect(url_for('admin.utilisateurs'))

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
    """Liste paginée des années académiques"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = AnneeAcademique.query
    if search:
        query = query.filter(
            (AnneeAcademique.nom.ilike(f'%{search}%')) |
            (AnneeAcademique.description.ilike(f'%{search}%'))
        )
    
    annees = query.order_by(AnneeAcademique.nom.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/annees_academiques.html', annees=annees, search=search)

@bp.route('/annees-academiques/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_annees_academiques():
    """Exporter les années académiques en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    annees = AnneeAcademique.query.order_by(AnneeAcademique.nom.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Nom', 'Description', 'Statut', 'Date début', 'Date fin'])
    
    for annee in annees:
        writer.writerow([
            annee.nom,
            annee.description or '',
            'Active' if annee.active else 'Inactive',
            annee.date_debut.strftime('%d/%m/%Y') if annee.date_debut else '',
            annee.date_fin.strftime('%d/%m/%Y') if annee.date_fin else ''
        ])
    
    output.seek(0)
    filename = f"annees_academiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/annees-academiques/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_annees_academiques():
    """Importer des années académiques depuis un fichier CSV"""
    import csv
    import io
    from datetime import datetime
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                if AnneeAcademique.query.filter_by(nom=row['Nom']).first():
                    erreurs.append(f"Année {row['Nom']} déjà existante")
                    continue
                
                annee = AnneeAcademique(
                    nom=row['Nom'],
                    description=row['Description'] if row['Description'] else None
                )
                
                if row['Date début']:
                    try:
                        annee.date_debut = datetime.strptime(row['Date début'], '%d/%m/%Y').date()
                    except:
                        pass
                
                if row['Date fin']:
                    try:
                        annee.date_fin = datetime.strptime(row['Date fin'], '%d/%m/%Y').date()
                    except:
                        pass
                
                db.session.add(annee)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} années académiques importées avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

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
    """Modifier une année académique existante"""
    annee = AnneeAcademique.query.get_or_404(annee_id)
    formulaire = FormulaireAnneeAcademique(obj=annee)
    
    if formulaire.validate_on_submit():
        try:
            annee.nom = formulaire.nom.data
            annee.date_debut = formulaire.date_debut.data
            annee.date_fin = formulaire.date_fin.data
            annee.active = formulaire.active.data
            
            db.session.commit()
            flash(f'Année académique "{annee.nom}" modifiée avec succès !', 'success')
            return redirect(url_for('admin.annees_academiques'))
            
        except Exception as e:
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('admin/modifier_annee_academique.html', formulaire=formulaire, annee=annee)

@bp.route('/semestres')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def semestres():
    """Liste paginée des semestres"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = Semestre.query
    if search:
        query = query.filter(
            (Semestre.code.ilike(f'%{search}%')) |
            (Semestre.nom.ilike(f'%{search}%'))
        )
    
    semestres = query.order_by(Semestre.code).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/semestres.html', semestres=semestres, search=search)

@bp.route('/semestres/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_semestres():
    """Exporter les semestres en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    semestres = Semestre.query.order_by(Semestre.code).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Code', 'Nom', 'Année académique', 'Statut', 'Date début', 'Date fin'])
    
    for semestre in semestres:
        writer.writerow([
            semestre.code,
            semestre.nom,
            semestre.annee_academique.nom if semestre.annee_academique else '',
            'Actif' if semestre.actif else 'Inactif',
            semestre.date_debut.strftime('%d/%m/%Y') if semestre.date_debut else '',
            semestre.date_fin.strftime('%d/%m/%Y') if semestre.date_fin else ''
        ])
    
    output.seek(0)
    filename = f"semestres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/semestres/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_semestres():
    """Importer des semestres depuis un fichier CSV"""
    import csv
    import io
    from datetime import datetime
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                if Semestre.query.filter_by(code=row['Code']).first():
                    erreurs.append(f"Code {row['Code']} déjà existant")
                    continue
                
                semestre = Semestre(
                    code=row['Code'],
                    nom=row['Nom']
                )
                
                if row['Date début']:
                    try:
                        semestre.date_debut = datetime.strptime(row['Date début'], '%d/%m/%Y').date()
                    except:
                        pass
                
                if row['Date fin']:
                    try:
                        semestre.date_fin = datetime.strptime(row['Date fin'], '%d/%m/%Y').date()
                    except:
                        pass
                
                db.session.add(semestre)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} semestres importés avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

@bp.route('/semestres/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_semestre():
    """Créer un nouveau semestre"""
    formulaire = FormulaireSemestre()
    
    # Remplir les choix d'années académiques
    annees = ServiceAcademique.obtenir_toutes_annees()
    formulaire.annee_academique_id.choices = [(a.id, a.nom) for a in annees]
    
    # Obtenir l'année active pour l'affichage
    annee_active = ServiceAcademique.obtenir_annee_active()
    
    if formulaire.validate_on_submit():
        semestre, succes = ServiceAcademique.creer_semestre(
            nom=formulaire.nom.data,
            code=formulaire.code.data,
            date_debut=formulaire.date_debut.data,
            date_fin=formulaire.date_fin.data,
            annee_id=formulaire.annee_academique_id.data,
            actif=formulaire.actif.data
        )
        
        if succes:
            flash(f'Semestre "{semestre.code}" créé avec succès !', 'success')
            return redirect(url_for('admin.semestres'))
        else:
            flash('Erreur lors de la création du semestre.', 'error')
    
    return render_template('admin/creer_semestre.html', formulaire=formulaire, annee_active=annee_active)

@bp.route('/semestres/<int:semestre_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_semestre(semestre_id):
    """Modifier un semestre existant"""
    semestre = Semestre.query.get_or_404(semestre_id)
    formulaire = FormulaireSemestre(obj=semestre)
    
    # Remplir les choix d'années académiques
    annees = ServiceAcademique.obtenir_toutes_annees()
    formulaire.annee_academique_id.choices = [(a.id, a.nom) for a in annees]
    
    if formulaire.validate_on_submit():
        succes = ServiceAcademique.modifier_semestre(
            semestre_id=semestre_id,
            nom=formulaire.nom.data,
            code=formulaire.code.data,
            date_debut=formulaire.date_debut.data,
            date_fin=formulaire.date_fin.data,
            annee_id=formulaire.annee_academique_id.data,
            actif=formulaire.actif.data
        )
        
        if succes:
            flash(f'Semestre "{semestre.nom}" modifié avec succès !', 'success')
            return redirect(url_for('admin.semestres'))
        else:
            flash('Erreur lors de la modification du semestre.', 'error')
    
    return render_template('admin/modifier_semestre.html', formulaire=formulaire, semestre=semestre)

@bp.route('/semestres/<int:semestre_id>/activer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def activer_semestre(semestre_id):
    """Activer un semestre"""
    semestre = Semestre.query.get_or_404(semestre_id)
    
    try:
        # Désactiver tous les autres semestres de la même année
        autres_semestres = Semestre.query.filter(
            Semestre.annee_academique_id == semestre.annee_academique_id,
            Semestre.id != semestre_id
        ).all()
        
        for autre_semestre in autres_semestres:
            autre_semestre.actif = False
        
        # Activer le semestre sélectionné
        semestre.actif = True
        db.session.commit()
        
        flash(f'Semestre "{semestre.code}" activé avec succès !', 'success')
        return redirect(url_for('admin.semestres'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'activation: {str(e)}', 'error')
        return redirect(url_for('admin.semestres'))

@bp.route('/semestres/<int:semestre_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_semestre(semestre_id):
    """Supprimer un semestre"""
    semestre = Semestre.query.get_or_404(semestre_id)
    
    # Vérifier les dépendances
    dependances = []
    
    if semestre.unites_enseignement:
        dependances.append(f"{len(semestre.unites_enseignement)} unité(s) d'enseignement")
    
    if dependances:
        dependances_str = ", ".join(dependances)
        flash(f'Impossible de supprimer ce semestre car il contient : {dependances_str}. Veuillez d\'abord supprimer ces éléments.', 'error')
        return redirect(url_for('admin.semestres'))
    
    try:
        db.session.delete(semestre)
        db.session.commit()
        flash(f'Semestre "{semestre.code}" supprimé avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        # Message d'erreur plus spécifique pour les contraintes de clés étrangères
        if "foreign key constraint fails" in str(e):
            flash('Impossible de supprimer ce semestre car il est référencé par d\'autres éléments du système. Veuillez d\'abord supprimer tous les éléments liés.', 'error')
        else:
            flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.semestres'))

# ==================== GESTION DES UNITÉS D'ENSEIGNEMENT ====================

@bp.route('/unites-enseignement')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def unites_enseignement():
    """Liste paginée des unités d'enseignement"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = UniteEnseignement.query
    if search:
        query = query.filter(
            (UniteEnseignement.code.ilike(f'%{search}%')) |
            (UniteEnseignement.nom.ilike(f'%{search}%')) |
            (UniteEnseignement.description.ilike(f'%{search}%'))
        )
    
    unites = query.order_by(UniteEnseignement.code).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/unites_enseignement.html', unites=unites, search=search)

@bp.route('/unites-enseignement/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_unites_enseignement():
    """Exporter les unités d'enseignement en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    unites = UniteEnseignement.query.order_by(UniteEnseignement.code).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Code', 'Nom', 'Description', 'Coefficient', 'Semestre', 'Année académique'])
    
    for unite in unites:
        writer.writerow([
            unite.code,
            unite.nom,
            unite.description or '',
            unite.coefficient,
            unite.semestre.nom if unite.semestre else '',
            unite.annee_academique.nom if unite.annee_academique else ''
        ])
    
    output.seek(0)
    filename = f"unites_enseignement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/unites-enseignement/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_unites_enseignement():
    """Importer des unités d'enseignement depuis un fichier CSV"""
    import csv
    import io
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                if UniteEnseignement.query.filter_by(code=row['Code']).first():
                    erreurs.append(f"Code {row['Code']} déjà existant")
                    continue
                
                unite = UniteEnseignement(
                    code=row['Code'],
                    nom=row['Nom'],
                    description=row['Description'] if row['Description'] else None,
                    coefficient=float(row['Coefficient']) if row['Coefficient'] else 1.0
                )
                
                db.session.add(unite)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} unités d'enseignement importées avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

@bp.route('/unites-enseignement/<int:ue_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_unite_enseignement(ue_id):
    """Modifier une unité d'enseignement existante"""
    ue = UniteEnseignement.query.get_or_404(ue_id)
    formulaire = FormulaireUniteEnseignement(obj=ue)
    
    # Remplir les choix de semestres
    semestres = ServiceAcademique.obtenir_tous_semestres()
    formulaire.semestre_id.choices = [(s.id, f"{s.code} - {s.nom}") for s in semestres]
    
    if formulaire.validate_on_submit():
        succes = ServiceAcademique.modifier_unite_enseignement(
            ue_id=ue_id,
            code=formulaire.code.data,
            nom=formulaire.nom.data,
            description=formulaire.description.data,
            credits=formulaire.credits.data,
            coefficient=formulaire.coefficient.data,
            semestre_id=formulaire.semestre_id.data
        )
        
        if succes:
            flash(f'Unité d\'enseignement "{ue.nom}" modifiée avec succès !', 'success')
            return redirect(url_for('admin.unites_enseignement'))
        else:
            flash('Erreur lors de la modification de l\'unité d\'enseignement.', 'error')
    
    return render_template('admin/modifier_unite_enseignement.html', formulaire=formulaire, ue=ue)

@bp.route('/unites-enseignement/<int:ue_id>/details')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def details_unite_enseignement(ue_id):
    """Détails d'une unité d'enseignement"""
    ue = UniteEnseignement.query.get_or_404(ue_id)
    matieres = ServiceAcademique.obtenir_matieres_par_ue(ue_id)
    
    return render_template('admin/details_unite_enseignement.html', ue=ue, matieres=matieres)

@bp.route('/unites-enseignement/<int:ue_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_unite_enseignement(ue_id):
    """Supprimer une unité d'enseignement"""
    ue = UniteEnseignement.query.get_or_404(ue_id)
    
    # Vérifier les dépendances
    dependances = []
    
    if ue.matieres:
        dependances.append(f"{len(ue.matieres)} matière(s)")
    
    if ue.groupes:
        dependances.append(f"{len(ue.groupes)} groupe(s)")
    
    if dependances:
        dependances_str = ", ".join(dependances)
        flash(f'Impossible de supprimer cette unité d\'enseignement car elle est liée à : {dependances_str}. Veuillez d\'abord supprimer ces éléments.', 'error')
        return redirect(url_for('admin.unites_enseignement'))
    
    try:
        db.session.delete(ue)
        db.session.commit()
        flash(f'Unité d\'enseignement "{ue.code}" supprimée avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        # Message d'erreur plus spécifique pour les contraintes de clés étrangères
        if "foreign key constraint fails" in str(e):
            flash('Impossible de supprimer cette unité d\'enseignement car elle est référencée par d\'autres éléments du système. Veuillez d\'abord supprimer tous les éléments liés.', 'error')
        else:
            flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.unites_enseignement'))

# ==================== GESTION DES MATIÈRES ====================

@bp.route('/matieres')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def matieres():
    """Liste paginée des matières"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = Matiere.query
    if search:
        query = query.filter(
            (Matiere.code.ilike(f'%{search}%')) |
            (Matiere.nom.ilike(f'%{search}%')) |
            (Matiere.description.ilike(f'%{search}%'))
        )
    
    matieres = query.order_by(Matiere.code).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/matieres.html', matieres=matieres, search=search)

@bp.route('/matieres/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_matieres():
    """Exporter les matières en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    matieres = Matiere.query.order_by(Matiere.code).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Code', 'Nom', 'Description', 'Coefficient', 'Volume horaire', 'Unité d\'enseignement', 'Enseignant'])
    
    for matiere in matieres:
        writer.writerow([
            matiere.code,
            matiere.nom,
            matiere.description or '',
            matiere.coefficient,
            matiere.volume_horaire or '',
            matiere.unite_enseignement.nom if matiere.unite_enseignement else '',
            matiere.enseignant.nom_complet if matiere.enseignant else ''
        ])
    
    output.seek(0)
    filename = f"matieres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/matieres/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_matieres():
    """Importer des matières depuis un fichier CSV"""
    import csv
    import io
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                if Matiere.query.filter_by(code=row['Code']).first():
                    erreurs.append(f"Code {row['Code']} déjà existant")
                    continue
                
                matiere = Matiere(
                    code=row['Code'],
                    nom=row['Nom'],
                    description=row['Description'] if row['Description'] else None,
                    coefficient=float(row['Coefficient']) if row['Coefficient'] else 1.0,
                    volume_horaire=int(row['Volume horaire']) if row['Volume horaire'] else None
                )
                
                db.session.add(matiere)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} matières importées avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

@bp.route('/matieres/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_matiere():
    """Créer une nouvelle matière"""
    formulaire = FormulaireMatiere()
    
    # Remplir les choix d'unités d'enseignement
    ues = ServiceAcademique.obtenir_toutes_unites_enseignement()
    formulaire.unite_enseignement_id.choices = [(ue.id, f"{ue.code} - {ue.nom}") for ue in ues]
    
    # Remplir les choix d'enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    formulaire.enseignant_id.choices = [('', '-- Sélectionner un enseignant --')] + [(e.id, f"{e.nom_complet} ({e.matricule})") for e in enseignants]
    
    # Obtenir l'année active pour l'affichage
    annee_active = ServiceAcademique.obtenir_annee_active()
    
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

@bp.route('/matieres/<int:matiere_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_matiere(matiere_id):
    """Modifier une matière existante"""
    matiere = Matiere.query.get_or_404(matiere_id)
    formulaire = FormulaireMatiere(obj=matiere)
    
    # Remplir les choix d'unités d'enseignement
    ues = ServiceAcademique.obtenir_toutes_unites_enseignement()
    formulaire.unite_enseignement_id.choices = [(ue.id, f"{ue.code} - {ue.nom}") for ue in ues]
    
    # Remplir les choix d'enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    formulaire.enseignant_id.choices = [('', '-- Sélectionner un enseignant --')] + [(e.id, f"{e.nom_complet} ({e.matricule})") for e in enseignants]
    
    if formulaire.validate_on_submit():
        try:
            matiere.code = formulaire.code.data
            matiere.nom = formulaire.nom.data
            matiere.description = formulaire.description.data
            matiere.volume_horaire = formulaire.volume_horaire.data
            matiere.coefficient = formulaire.coefficient.data
            matiere.unite_enseignement_id = formulaire.unite_enseignement_id.data
            matiere.enseignant_id = formulaire.enseignant_id.data if formulaire.enseignant_id.data else None
            
            db.session.commit()
            flash(f'Matière "{matiere.code}" modifiée avec succès !', 'success')
            return redirect(url_for('admin.matieres'))
            
        except Exception as e:
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('admin/modifier_matiere.html', formulaire=formulaire, matiere=matiere)

@bp.route('/matieres/<int:matiere_id>/details')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def details_matiere(matiere_id):
    """Afficher les détails d'une matière"""
    matiere = Matiere.query.get_or_404(matiere_id)
    return render_template('admin/details_matiere.html', matiere=matiere)

@bp.route('/matieres/<int:matiere_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_matiere(matiere_id):
    """Supprimer une matière"""
    matiere = Matiere.query.get_or_404(matiere_id)
    
    try:
        db.session.delete(matiere)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Matière "{matiere.code}" supprimée avec succès !'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la suppression: {str(e)}'})

# ==================== GESTION DES ÉTUDIANTS ====================

@bp.route('/etudiants')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def etudiants():
    """Liste paginée des étudiants"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = Etudiant.query
    if search:
        query = query.filter(
            (Etudiant.nom.ilike(f'%{search}%')) |
            (Etudiant.prenom.ilike(f'%{search}%')) |
            (Etudiant.matricule.ilike(f'%{search}%')) |
            (Etudiant.email.ilike(f'%{search}%'))
        )
    
    etudiants = query.order_by(Etudiant.nom, Etudiant.prenom).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/etudiants.html', etudiants=etudiants, search=search)

@bp.route('/etudiants/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_etudiants():
    """Exporter les étudiants en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    # Récupérer tous les étudiants
    etudiants = Etudiant.query.order_by(Etudiant.nom, Etudiant.prenom).all()
    
    # Créer le fichier CSV en mémoire
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(['Matricule', 'Nom', 'Prénom', 'Date de naissance', 'Sexe', 'Email', 'Téléphone', 'Adresse', 'Statut', 'Année académique', 'Groupe'])
    
    # Données
    for etudiant in etudiants:
        writer.writerow([
            etudiant.matricule,
            etudiant.nom,
            etudiant.prenom,
            etudiant.date_naissance.strftime('%d/%m/%Y') if etudiant.date_naissance else '',
            etudiant.sexe or '',
            etudiant.email or '',
            etudiant.telephone or '',
            etudiant.adresse or '',
            etudiant.statut or '',
            etudiant.annee_academique.nom if etudiant.annee_academique else '',
            etudiant.groupe.nom if etudiant.groupe else ''
        ])
    
    output.seek(0)
    
    # Créer le fichier temporaire
    filename = f"etudiants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/etudiants/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_etudiants():
    """Importer des étudiants depuis un fichier CSV"""
    import csv
    import io
    from datetime import datetime
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        # Lire le fichier CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                # Vérifier si l'étudiant existe déjà
                if Etudiant.query.filter_by(matricule=row['Matricule']).first():
                    erreurs.append(f"Matricule {row['Matricule']} déjà existant")
                    continue
                
                # Créer l'étudiant
                etudiant = Etudiant(
                    matricule=row['Matricule'],
                    nom=row['Nom'],
                    prenom=row['Prénom'],
                    email=row['Email'] if row['Email'] else None,
                    telephone=row['Téléphone'] if row['Téléphone'] else None,
                    adresse=row['Adresse'] if row['Adresse'] else None,
                    statut=row['Statut'] if row['Statut'] else 'actif'
                )
                
                # Traiter la date de naissance
                if row['Date de naissance']:
                    try:
                        etudiant.date_naissance = datetime.strptime(row['Date de naissance'], '%d/%m/%Y').date()
                    except:
                        pass
                
                # Traiter le sexe
                if row['Sexe']:
                    etudiant.sexe = row['Sexe'].lower()
                
                db.session.add(etudiant)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} étudiants importés avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

@bp.route('/etudiants/rechercher')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def rechercher_etudiants():
    """Rechercher des étudiants"""
    query = request.args.get('q', '')
    if query:
        etudiants = Etudiant.query.filter(
            (Etudiant.nom.ilike(f'%{query}%')) |
            (Etudiant.prenom.ilike(f'%{query}%')) |
            (Etudiant.matricule.ilike(f'%{query}%'))
        ).all()
    else:
        etudiants = []
    
    return render_template('admin/rechercher_etudiants.html', etudiants=etudiants, query=query)

@bp.route('/etudiants/<int:etudiant_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_etudiant(etudiant_id):
    """Modifier un étudiant existant"""
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    formulaire = FormulaireEtudiant(obj=etudiant, etudiant_existant=etudiant)
    
    if formulaire.validate_on_submit():
        try:
            # Utiliser la méthode du service pour la modification
            etudiant_modifie, succes = ServiceAcademique.modifier_etudiant(
                etudiant_id=etudiant_id,
                matricule=formulaire.matricule.data,
                nom=formulaire.nom.data,
                prenom=formulaire.prenom.data,
                date_naissance=formulaire.date_naissance.data,
                sexe=formulaire.sexe.data,
                lieu_naissance=formulaire.lieu_naissance.data,
                adresse=formulaire.adresse.data,
                telephone=formulaire.telephone.data,
                email=formulaire.email.data,
                statut=formulaire.statut.data
            )
            
            if succes and etudiant_modifie:
                flash(f'Étudiant "{etudiant_modifie.nom_complet}" modifié avec succès !', 'success')
                return redirect(url_for('admin.etudiants'))
            else:
                flash('Erreur lors de la modification. Vérifiez que le matricule et l\'email sont uniques.', 'error')
            
        except Exception as e:
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('admin/modifier_etudiant.html', formulaire=formulaire, etudiant=etudiant)

@bp.route('/etudiants/<int:etudiant_id>/profil')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def profil_etudiant(etudiant_id):
    """Voir le profil d'un étudiant"""
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    
    # Récupérer les informations supplémentaires
    notes = ServicePedagogique.obtenir_notes_etudiant(etudiant_id)
    absences = ServicePedagogique.obtenir_absences_etudiant(etudiant_id)
    
    return render_template('admin/profil_etudiant.html', 
                         etudiant=etudiant, 
                         notes=notes, 
                         absences=absences)

# ==================== GESTION DES ENSEIGNANTS ====================

@bp.route('/enseignants')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def enseignants():
    """Liste paginée des enseignants"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = Enseignant.query
    if search:
        query = query.filter(
            (Enseignant.nom.ilike(f'%{search}%')) |
            (Enseignant.prenom.ilike(f'%{search}%')) |
            (Enseignant.matricule.ilike(f'%{search}%')) |
            (Enseignant.email.ilike(f'%{search}%')) |
            (Enseignant.specialite.ilike(f'%{search}%'))
        )
    
    enseignants = query.order_by(Enseignant.nom, Enseignant.prenom).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/enseignants.html', enseignants=enseignants, search=search)

@bp.route('/enseignants/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_enseignants():
    """Exporter les enseignants en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    enseignants = Enseignant.query.order_by(Enseignant.nom, Enseignant.prenom).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Matricule', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Spécialité', 'Grade', 'Date d\'embauche', 'Statut'])
    
    for enseignant in enseignants:
        writer.writerow([
            enseignant.matricule,
            enseignant.nom,
            enseignant.prenom,
            enseignant.email or '',
            enseignant.telephone or '',
            enseignant.specialite or '',
            enseignant.grade or '',
            enseignant.date_embauche.strftime('%d/%m/%Y') if enseignant.date_embauche else '',
            enseignant.statut or ''
        ])
    
    output.seek(0)
    filename = f"enseignants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/enseignants/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_enseignants():
    """Importer des enseignants depuis un fichier CSV"""
    import csv
    import io
    from datetime import datetime
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                if Enseignant.query.filter_by(matricule=row['Matricule']).first():
                    erreurs.append(f"Matricule {row['Matricule']} déjà existant")
                    continue
                
                enseignant = Enseignant(
                    matricule=row['Matricule'],
                    nom=row['Nom'],
                    prenom=row['Prénom'],
                    email=row['Email'] if row['Email'] else None,
                    telephone=row['Téléphone'] if row['Téléphone'] else None,
                    specialite=row['Spécialité'] if row['Spécialité'] else None,
                    grade=row['Grade'] if row['Grade'] else None,
                    statut=row['Statut'] if row['Statut'] else 'actif'
                )
                
                if row['Date d\'embauche']:
                    try:
                        enseignant.date_embauche = datetime.strptime(row['Date d\'embauche'], '%d/%m/%Y').date()
                    except:
                        pass
                
                db.session.add(enseignant)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} enseignants importés avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

@bp.route('/enseignants/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_enseignant():
    """Créer un nouvel enseignant"""
    formulaire = FormulaireEnseignant()
    
    if formulaire.validate_on_submit():
        try:
            # Créer l'enseignant
            enseignant = Enseignant(
                matricule=formulaire.matricule.data,
                nom=formulaire.nom.data,
                prenom=formulaire.prenom.data,
                date_naissance=formulaire.date_naissance.data,
                sexe=formulaire.sexe.data,
                specialite=formulaire.specialite.data,
                grade=formulaire.grade.data,
                telephone=formulaire.telephone.data,
                email=formulaire.email.data,
                adresse=formulaire.adresse.data,
                date_embauche=formulaire.date_embauche.data
            )
            
            db.session.add(enseignant)
            db.session.commit()
            
            # Créer automatiquement un compte utilisateur lié
            from app.services.authentification import ServiceAuthentification
            service_auth = ServiceAuthentification()
            
            # Générer un mot de passe temporaire
            mot_de_passe_temp = f"enseignant{enseignant.matricule}"
            
            utilisateur, succes = service_auth.creer_utilisateur(
                nom=enseignant.nom,
                prenom=enseignant.prenom,
                email=enseignant.email,
                mot_de_passe=mot_de_passe_temp,
                role='enseignant'
            )
            
            if succes and utilisateur:
                # Lier l'utilisateur à l'enseignant
                enseignant.utilisateur_id = utilisateur.id
                db.session.commit()
                
                flash(f'Enseignant "{enseignant.nom_complet}" créé avec succès ! Compte utilisateur créé avec le mot de passe temporaire: {mot_de_passe_temp}', 'success')
            else:
                flash(f'Enseignant "{enseignant.nom_complet}" créé mais erreur lors de la création du compte utilisateur.', 'warning')
            
            return redirect(url_for('admin.enseignants'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'error')
    
    return render_template('admin/creer_enseignant.html', formulaire=formulaire)

@bp.route('/enseignants/<int:enseignant_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_enseignant(enseignant_id):
    """Modifier un enseignant existant"""
    enseignant = Enseignant.query.get_or_404(enseignant_id)
    formulaire = FormulaireEnseignant(obj=enseignant, enseignant_existant=enseignant)
    
    if formulaire.validate_on_submit():
        try:
            # Utiliser la méthode du service pour la modification
            enseignant_modifie, succes = ServiceAcademique.modifier_enseignant(
                enseignant_id=enseignant_id,
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
                grade=formulaire.grade.data,
                statut=formulaire.statut.data
            )
            
            if succes and enseignant_modifie:
                flash(f'Enseignant "{enseignant_modifie.nom_complet}" modifié avec succès !', 'success')
                return redirect(url_for('admin.enseignants'))
            else:
                flash('Erreur lors de la modification. Vérifiez que le matricule et l\'email sont uniques.', 'error')
            
        except Exception as e:
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('admin/modifier_enseignant.html', formulaire=formulaire, enseignant=enseignant)

@bp.route('/enseignants/<int:enseignant_id>/details')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def details_enseignant(enseignant_id):
    """Afficher les détails d'un enseignant"""
    from datetime import date
    
    enseignant = Enseignant.query.get_or_404(enseignant_id)
    matieres = ServiceAcademique.obtenir_matieres_par_enseignant(enseignant_id)
    
    # Calculer l'ancienneté
    aujourd_hui = date.today()
    anciennete = aujourd_hui.year - enseignant.date_embauche.year
    if aujourd_hui.month < enseignant.date_embauche.month or (aujourd_hui.month == enseignant.date_embauche.month and aujourd_hui.day < enseignant.date_embauche.day):
        anciennete -= 1
    
    return render_template('admin/details_enseignant.html', enseignant=enseignant, anciennete=anciennete)

@bp.route('/enseignants/<int:enseignant_id>/statut/<statut>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def changer_statut_enseignant(enseignant_id, statut):
    """Change le statut d'un enseignant"""
    try:
        enseignant, succes = ServiceAcademique.changer_statut_enseignant(enseignant_id, statut)
        
        if succes and enseignant:
            statut_nom = {
                'actif': 'Actif',
                'inactif': 'Inactif', 
                'retraite': 'Retraite',
                'demissionne': 'Demissionne'
            }.get(statut, statut)
            
            flash(f'Statut de l\'enseignant "{enseignant.prenom} {enseignant.nom}" changé vers "{statut_nom}" avec succès', 'success')
        else:
            flash('Erreur lors du changement de statut de l\'enseignant', 'error')
            
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('admin.enseignants'))

# ==================== GESTION DES GROUPES ====================

@bp.route('/groupes')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def groupes():
    """Liste paginée des groupes"""
    page = request.args.get('page', 1, type=int)
    per_page = 25
    search = request.args.get('search', '')
    
    query = Groupe.query
    if search:
        query = query.filter(
            (Groupe.nom.ilike(f'%{search}%')) |
            (Groupe.code.ilike(f'%{search}%')) |
            (Groupe.description.ilike(f'%{search}%'))
        )
    
    groupes = query.order_by(Groupe.nom).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/groupes.html', groupes=groupes, search=search)

@bp.route('/groupes/export')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def exporter_groupes():
    """Exporter les groupes en CSV"""
    from flask import send_file
    import csv
    import io
    from datetime import datetime
    
    groupes = Groupe.query.order_by(Groupe.nom).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Code', 'Nom', 'Description', 'Effectif', 'Année académique', 'Semestre'])
    
    for groupe in groupes:
        writer.writerow([
            groupe.code,
            groupe.nom,
            groupe.description or '',
            len(groupe.etudiants) if groupe.etudiants else 0,
            groupe.annee_academique.nom if groupe.annee_academique else '',
            groupe.semestre.nom if groupe.semestre else ''
        ])
    
    output.seek(0)
    filename = f"groupes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/groupes/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_groupes():
    """Importer des groupes depuis un fichier CSV"""
    import csv
    import io
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Format de fichier non supporté. Utilisez un fichier CSV.'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        compteur = 0
        erreurs = []
        
        for row in csv_reader:
            try:
                if Groupe.query.filter_by(code=row['Code']).first():
                    erreurs.append(f"Code {row['Code']} déjà existant")
                    continue
                
                groupe = Groupe(
                    code=row['Code'],
                    nom=row['Nom'],
                    description=row['Description'] if row['Description'] else None
                )
                
                db.session.add(groupe)
                compteur += 1
                
            except Exception as e:
                erreurs.append(f"Erreur ligne {compteur + 1}: {str(e)}")
        
        db.session.commit()
        
        message = f"{compteur} groupes importés avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreurs rencontrées."
        
        return jsonify({'success': True, 'message': message, 'erreurs': erreurs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors de l\'import: {str(e)}'})

@bp.route('/pedagogique')
@login_required
@administrateur_requis
def pedagogique_dashboard():
    """Tableau de bord pédagogique"""
    # Statistiques pédagogiques
    total_etudiants = Etudiant.query.count()
    total_enseignants = Enseignant.query.count()
    total_groupes = Groupe.query.count()
    total_ues = UniteEnseignement.query.count()
    
    # Dernières activités
    derniers_groupes = Groupe.query.order_by(Groupe.date_creation.desc()).limit(5).all()
    
    return render_template('admin/pedagogique/dashboard.html',
                         total_etudiants=total_etudiants,
                         total_enseignants=total_enseignants,
                         total_groupes=total_groupes,
                         total_ues=total_ues,
                         derniers_groupes=derniers_groupes)

@bp.route('/pedagogique/dashboard')
@login_required
@administrateur_requis
def pedagogique_dashboard_redirect():
    """Redirection vers le dashboard pédagogique"""
    return redirect(url_for('admin.pedagogique_dashboard'))

@bp.route('/pedagogique/notes')
@login_required
@administrateur_requis
def validation_notes():
    """Validation des notes"""
    # Récupérer les notes en attente de validation
    from app.models.pedagogique import Note
    
    notes_en_attente = Note.query.filter_by(validee=False).all()
    
    return render_template('admin/pedagogique/validation_notes.html', 
                         notes_en_attente=notes_en_attente)

@bp.route('/pedagogique/notes/<int:note_id>/valider', methods=['POST'])
@login_required
@administrateur_requis
def valider_note(note_id):
    """Valider une note"""
    from app.models.pedagogique import Note
    
    note = Note.query.get_or_404(note_id)
    
    try:
        note.validee = True
        note.date_validation = datetime.now()
        note.validateur_id = current_user.id
        
        db.session.commit()
        flash('Note validée avec succès !', 'success')
        
    except Exception as e:
        flash(f'Erreur lors de la validation: {str(e)}', 'error')
    
    return redirect(url_for('admin.validation_notes'))

@bp.route('/pedagogique/deliberations')
@login_required
@administrateur_requis
def deliberations():
    """Liste des délibérations"""
    from app.models.pedagogique import Deliberation
    
    deliberations = Deliberation.query.order_by(Deliberation.date_creation.desc()).all()
    
    return render_template('admin/pedagogique/deliberations.html', 
                         deliberations=deliberations)

@bp.route('/pedagogique/deliberations/<int:deliberation_id>')
@login_required
@administrateur_requis
def detail_deliberation(deliberation_id):
    """Détails d'une délibération"""
    from app.models.pedagogique import Deliberation
    
    deliberation = Deliberation.query.get_or_404(deliberation_id)
    
    return render_template('admin/pedagogique/detail_deliberation.html', 
                         deliberation=deliberation)

@bp.route('/pedagogique/deliberations/<int:deliberation_id>/calculer', methods=['POST'])
@login_required
@administrateur_requis
def calculer_deliberation(deliberation_id):
    """Calculer les résultats d'une délibération"""
    from app.models.pedagogique import Deliberation
    
    deliberation = Deliberation.query.get_or_404(deliberation_id)
    
    try:
        # Logique de calcul des résultats
        deliberation.statut = 'en_cours'
        db.session.commit()
        
        flash('Calcul des résultats en cours...', 'info')
        
    except Exception as e:
        flash(f'Erreur lors du calcul: {str(e)}', 'error')
    
    return redirect(url_for('admin.detail_deliberation', deliberation_id=deliberation_id))

@bp.route('/pedagogique/deliberations/<int:deliberation_id>/valider', methods=['POST'])
@login_required
@administrateur_requis
def valider_deliberation(deliberation_id):
    """Valider une délibération"""
    from app.models.pedagogique import Deliberation
    
    deliberation = Deliberation.query.get_or_404(deliberation_id)
    
    try:
        deliberation.statut = 'validee'
        deliberation.date_validation = datetime.now()
        deliberation.validateur_id = current_user.id
        
        db.session.commit()
        flash('Délibération validée avec succès !', 'success')
        
    except Exception as e:
        flash(f'Erreur lors de la validation: {str(e)}', 'error')
    
    return redirect(url_for('admin.detail_deliberation', deliberation_id=deliberation_id))

@bp.route('/pedagogique/rapports')
@login_required
@administrateur_requis
def rapports_pedagogiques():
    """Rapports pédagogiques"""
    # Statistiques pour les rapports
    total_etudiants = Etudiant.query.count()
    total_enseignants = Enseignant.query.count()
    total_groupes = Groupe.query.count()
    
    # Répartition par sexe
    etudiants_hommes = Etudiant.query.filter_by(sexe='M').count()
    etudiants_femmes = Etudiant.query.filter_by(sexe='F').count()
    
    return render_template('admin/pedagogique/rapports.html',
                         total_etudiants=total_etudiants,
                         total_enseignants=total_enseignants,
                         total_groupes=total_groupes,
                         etudiants_hommes=etudiants_hommes,
                         etudiants_femmes=etudiants_femmes)

@bp.route('/pedagogique/rapports/etudiant/<int:etudiant_id>')
@login_required
@administrateur_requis
def rapport_etudiant(etudiant_id):
    """Rapport détaillé d'un étudiant"""
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    
    # Récupérer les notes de l'étudiant
    from app.models.pedagogique import Note
    
    notes = Note.query.filter_by(etudiant_id=etudiant_id).all()
    
    # Calculer les moyennes
    if notes:
        moyenne_generale = sum(note.valeur * note.coefficient for note in notes) / sum(note.coefficient for note in notes)
    else:
        moyenne_generale = 0
    
    return render_template('admin/pedagogique/rapport_etudiant.html',
                         etudiant=etudiant,
                         notes=notes,
                         moyenne_generale=moyenne_generale)

# ==================== GESTION DES NOTIFICATIONS ====================

@bp.route('/notifications')
@login_required
@administrateur_requis
def notifications():
    """Liste des notifications"""
    notifications = ServiceNotification.get_all_notifications()
    return render_template('admin/notifications/liste.html', notifications=notifications)

@bp.route('/notifications/<int:notification_id>/marquer-lue')
@login_required
@administrateur_requis
def marquer_notification_lue(notification_id):
    """Marquer une notification comme lue"""
    notification = ServiceNotification.get_notification_by_id(notification_id)
    
    if notification:
        ServiceNotification.marquer_comme_lue(notification_id)
        flash('Notification marquée comme lue', 'success')
    else:
        flash('Notification non trouvée', 'error')
    
    return redirect(url_for('admin.notifications'))

@bp.route('/notifications/<int:notification_id>/supprimer')
@login_required
@administrateur_requis
def supprimer_notification(notification_id):
    """Supprimer une notification"""
    notification = ServiceNotification.get_notification_by_id(notification_id)
    
    if notification:
        ServiceNotification.supprimer_notification(notification_id)
        flash('Notification supprimée avec succès', 'success')
    else:
        flash('Notification non trouvée', 'error')
    
    return redirect(url_for('admin.notifications'))

@bp.route('/notifications/envoyer', methods=['GET', 'POST'])
@login_required
@administrateur_requis
def envoyer_notification():
    """Envoyer une notification"""
    from app.forms.notification import FormulaireNotification
    
    formulaire = FormulaireNotification()
    
    if formulaire.validate_on_submit():
        try:
            # Créer la notification
            notification = ServiceNotification.creer_notification(
                titre=formulaire.titre.data,
                contenu=formulaire.contenu.data,
                type_notification=formulaire.type_notification.data,
                destinataires=formulaire.destinataires.data,
                expediteur_id=current_user.id
            )
            
            flash('Notification envoyée avec succès !', 'success')
            return redirect(url_for('admin.notifications'))
            
        except Exception as e:
            flash(f'Erreur lors de l\'envoi: {str(e)}', 'error')
    
    return render_template('admin/notifications/envoyer.html', formulaire=formulaire)

@bp.route('/notifications/liste')
@login_required
@administrateur_requis
def liste_notifications():
    """Liste complète des notifications"""
    notifications = ServiceNotification.get_all_notifications()
    return render_template('admin/notifications/liste.html', notifications=notifications)

@bp.route('/unites-enseignement/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_unite_enseignement():
    """Créer une nouvelle unité d'enseignement"""
    formulaire = FormulaireUniteEnseignement()
    
    # Remplir les choix de semestres
    semestres = ServiceAcademique.obtenir_tous_semestres()
    formulaire.semestre_id.choices = [(s.id, f"{s.code} - {s.nom}") for s in semestres]
    
    # Obtenir l'année active pour l'affichage
    annee_active = ServiceAcademique.obtenir_annee_active()
    
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
    
    return render_template('admin/creer_unite_enseignement.html', formulaire=formulaire, semestres=semestres, annee_active=annee_active)

@bp.route('/unites-enseignement/<int:ue_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_unite_enseignement(ue_id):
    """Supprimer une unité d'enseignement"""
    ue = UniteEnseignement.query.get_or_404(ue_id)
    
    # Vérifier les dépendances
    dependances = []
    
    if ue.matieres:
        dependances.append(f"{len(ue.matieres)} matière(s)")
    
    if ue.groupes:
        dependances.append(f"{len(ue.groupes)} groupe(s)")
    
    if dependances:
        dependances_str = ", ".join(dependances)
        flash(f'Impossible de supprimer cette unité d\'enseignement car elle est liée à : {dependances_str}. Veuillez d\'abord supprimer ces éléments.', 'error')
        return redirect(url_for('admin.unites_enseignement'))
    
    try:
        db.session.delete(ue)
        db.session.commit()
        flash(f'Unité d\'enseignement "{ue.code}" supprimée avec succès !', 'success')
        
    except Exception as e:
        db.session.rollback()
        # Message d'erreur plus spécifique pour les contraintes de clés étrangères
        if "foreign key constraint fails" in str(e):
            flash('Impossible de supprimer cette unité d\'enseignement car elle est référencée par d\'autres éléments du système. Veuillez d\'abord supprimer tous les éléments liés.', 'error')
        else:
            flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.unites_enseignement'))

@bp.route('/groupes/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_groupe():
    """Créer un nouveau groupe"""
    formulaire = FormulaireGroupe()
    
    # Remplir les choix d'unités d'enseignement
    ues = ServiceAcademique.obtenir_toutes_unites_enseignement()
    formulaire.unite_enseignement_id.choices = [(ue.id, f"{ue.code} - {ue.nom}") for ue in ues]
    
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
    
    return render_template('admin/creer_groupe.html', formulaire=formulaire, annee_active=ServiceAcademique.obtenir_annee_active())
  