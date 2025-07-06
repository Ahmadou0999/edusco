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
    FormulaireMatiere, FormulaireEtudiant, FormulaireEnseignant, FormulaireGroupe,
    FormulaireGroupeGenerique, FormulaireUtilisationGroupeUE
)
from app.models.academique import AnneeAcademique, Semestre, UniteEnseignement, Matiere, Etudiant, Enseignant, Groupe
from app.extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy.sql import func, case
from app.services.notification import ServiceNotification
from app.services.pedagogique import ServicePedagogique
from app.models.utilisateur import Utilisateur
from app.models.pedagogique import Note
from app.models.academique import InscriptionGroupe

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

@bp.route('/utilisateurs/import', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def importer_utilisateurs():
    """Importer des utilisateurs depuis un fichier CSV"""
    from flask import jsonify
    import csv
    import io
    from app.services.authentification import ServiceAuthentification
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Le fichier doit être au format CSV'})
    
    try:
        # Lire le fichier CSV
        content = file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        service_auth = ServiceAuthentification()
        utilisateurs_crees = 0
        erreurs = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Commencer à 2 car ligne 1 = en-têtes
            try:
                # Vérifier les champs requis
                if not row.get('Nom') or not row.get('Prénom') or not row.get('Email'):
                    erreurs.append(f"Ligne {row_num}: Nom, Prénom et Email sont requis")
                    continue
                
                # Créer l'utilisateur
                utilisateur, succes = service_auth.creer_utilisateur(
                    nom=row['Nom'].strip(),
                    prenom=row['Prénom'].strip(),
                    email=row['Email'].strip(),
                    mot_de_passe='password123',  # Mot de passe par défaut
                    role=row.get('Rôle', 'etudiant').strip().lower()
                )
                
                if succes and utilisateur:
                    # Activer le compte si spécifié
                    if row.get('Statut', '').strip().lower() == 'actif':
                        utilisateur.actif = True
                        db.session.commit()
                    
                    utilisateurs_crees += 1
                else:
                    erreurs.append(f"Ligne {row_num}: Erreur lors de la création de l'utilisateur")
                    
            except Exception as e:
                erreurs.append(f"Ligne {row_num}: {str(e)}")
        
        message = f"{utilisateurs_crees} utilisateur(s) créé(s) avec succès"
        if erreurs:
            message += f". {len(erreurs)} erreur(s) rencontrée(s)"
        
        return jsonify({
            'success': True, 
            'message': message,
            'utilisateurs_crees': utilisateurs_crees,
            'erreurs': erreurs
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur lors du traitement du fichier: {str(e)}'})

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
    """Modifier une année académique"""
    annee = AnneeAcademique.query.get_or_404(annee_id)
    form = FormulaireAnneeAcademique(obj=annee)
    
    if form.validate_on_submit():
        annee.nom = form.nom.data
        annee.date_debut = form.date_debut.data
        annee.date_fin = form.date_fin.data
        annee.active = form.active.data
        
        db.session.commit()
        flash('Année académique modifiée avec succès.', 'success')
        return redirect(url_for('admin.annees_academiques'))
    
    return render_template('admin/modifier_annee_academique.html', form=form, annee=annee)

@bp.route('/annees-academiques/<int:annee_id>/details')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def details_annee_academique(annee_id):
    """Afficher les détails d'une année académique"""
    annee = AnneeAcademique.query.get_or_404(annee_id)
    
    # Statistiques de l'année
    enseignants = set()
    matieres = set()
    
    # Récupérer les enseignants via les inscriptions aux groupes
    for etudiant in annee.etudiants:
        for inscription in etudiant.inscriptions_groupes:
            if inscription.groupe and inscription.groupe.enseignant_responsable:
                enseignants.add(inscription.groupe.enseignant_responsable)
    
    # Récupérer les matières via les semestres et unités d'enseignement
    for semestre in annee.semestres:
        for ue in semestre.unites_enseignement:
            for matiere in ue.matieres:
                matieres.add(matiere)
    
    stats = {
        'total_semestres': len(annee.semestres),
        'total_etudiants': len(annee.etudiants),
        'total_enseignants': len(enseignants),
        'total_matieres': len(matieres)
    }
    
    return render_template('admin/details_annee_academique.html', annee=annee, stats=stats)

@bp.route('/annees-academiques/<int:annee_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_annee_academique(annee_id):
    """Supprimer une année académique"""
    annee = AnneeAcademique.query.get_or_404(annee_id)
    
    # Vérifications de sécurité
    if annee.active:
        flash('Impossible de supprimer une année académique active.', 'error')
        return redirect(url_for('admin.annees_academiques'))
    
    if annee.semestres:
        flash('Impossible de supprimer une année académique qui contient des semestres.', 'error')
        return redirect(url_for('admin.annees_academiques'))
    
    if annee.etudiants:
        flash('Impossible de supprimer une année académique qui contient des étudiants.', 'error')
        return redirect(url_for('admin.annees_academiques'))
    
    try:
        db.session.delete(annee)
        db.session.commit()
        flash('Année académique supprimée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression de l\'année académique.', 'error')
    
    return redirect(url_for('admin.annees_academiques'))

@bp.route('/annees-academiques/<int:annee_id>/activer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def activer_annee_academique(annee_id):
    """Activer une année académique"""
    annee = AnneeAcademique.query.get_or_404(annee_id)
    
    try:
        # Désactiver toutes les autres années
        AnneeAcademique.query.update({AnneeAcademique.active: False})
        
        # Activer l'année sélectionnée
        annee.active = True
        db.session.commit()
        
        flash(f'Année académique "{annee.nom}" activée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de l\'activation de l\'année académique.', 'error')
    
    return redirect(url_for('admin.annees_academiques'))

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
    
    # Obtenir l'année active pour l'affichage
    annee_active = ServiceAcademique.obtenir_annee_active()
    
    return render_template('admin/semestres.html', semestres=semestres, search=search, annee_active=annee_active)

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
    formulaire.annee_academique_id.choices = [(a.id, f"{a.nom} ({a.date_debut.year}-{a.date_fin.year})") for a in annees]
    
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
    formulaire.annee_academique_id.choices = [(a.id, f"{a.nom} ({a.date_debut.year}-{a.date_fin.year})") for a in annees]
    
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
    """Liste des unités d'enseignement organisées par semestre"""
    # Obtenir l'année active
    annee_active = ServiceAcademique.obtenir_annee_active()
    
    if annee_active:
        # Obtenir tous les semestres de l'année active avec leurs unités d'enseignement
        semestres = ServiceAcademique.obtenir_semestres_par_annee(annee_active.id)
        
        # Pour chaque semestre, charger ses unités d'enseignement
        for semestre in semestres:
            semestre.unites_enseignement = UniteEnseignement.query.filter_by(semestre_id=semestre.id).order_by(UniteEnseignement.code).all()
    else:
        semestres = []
    
    return render_template('admin/unites_enseignement.html', annee_active=annee_active, semestres=semestres)

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

@bp.route('/unites-enseignement/creer/<int:semestre_id>', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_unite_enseignement_semestre(semestre_id):
    """Créer une nouvelle unité d'enseignement pour un semestre spécifique"""
    # Vérifier que le semestre existe
    semestre = Semestre.query.get_or_404(semestre_id)
    
    formulaire = FormulaireUniteEnseignement()
    
    # Pré-remplir le semestre
    formulaire.semestre_id.data = semestre_id
    
    # Remplir les choix de semestres (pour la validation)
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
            semestre_id=semestre_id  # Utiliser le semestre pré-défini
        )
        
        if succes:
            flash(f'Unité d\'enseignement "{ue.code}" créée avec succès pour le semestre {semestre.nom} !', 'success')
            return redirect(url_for('admin.unites_enseignement'))
        else:
            flash('Erreur lors de la création de l\'unité d\'enseignement.', 'error')
    
    return render_template('admin/creer_unite_enseignement.html', 
                         formulaire=formulaire, 
                         semestres=semestres, 
                         annee_active=annee_active,
                         semestre_predefini=semestre)

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

@bp.route('/matieres/creer/<int:ue_id>', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_matiere_ue(ue_id):
    """Créer une nouvelle matière pour une UE spécifique"""
    # Vérifier que l'UE existe
    ue = UniteEnseignement.query.get_or_404(ue_id)
    
    formulaire = FormulaireMatiere()
    
    # Pré-remplir l'UE
    formulaire.unite_enseignement_id.data = ue_id
    
    # Remplir les choix d'unités d'enseignement (pour la validation)
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
            ue_id=ue_id,  # Utiliser l'UE pré-définie
            enseignant_id=formulaire.enseignant_id.data if formulaire.enseignant_id.data else None
        )
        
        if succes:
            flash(f'Matière "{matiere.code}" créée avec succès pour l\'UE {ue.code} !', 'success')
            return redirect(url_for('admin.matieres'))
        else:
            flash('Erreur lors de la création de la matière.', 'error')
    
    return render_template('admin/creer_matiere.html', 
                         formulaire=formulaire, 
                         annee_active=annee_active,
                         ue_predefinie=ue)

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
    
    # Récupérer les données pour les filtres
    from app.models.academique import Groupe, AnneeAcademique
    groupes = Groupe.query.all()
    annees_academiques = AnneeAcademique.query.all()
    
    return render_template('admin/etudiants.html', 
                         etudiants=etudiants, 
                         search=search,
                         groupes=groupes,
                         annees_academiques=annees_academiques)

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
            
            # Gérer la modification du mot de passe si fourni
            if formulaire.mot_de_passe.data and formulaire.confirmer_mot_de_passe.data:
                if etudiant.utilisateur:
                    from werkzeug.security import generate_password_hash
                    etudiant.utilisateur.mot_de_passe = generate_password_hash(formulaire.mot_de_passe.data)
                    db.session.commit()
                    flash('Mot de passe mis à jour avec succès !', 'success')
            
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
    """Afficher le profil détaillé d'un étudiant"""
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    return render_template('admin/profil_etudiant.html', etudiant=etudiant)

@bp.route('/etudiants/supprimer/<int:etudiant_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_etudiant(etudiant_id):
    """Supprimer un étudiant"""
    from flask import jsonify
    
    try:
        etudiant = Etudiant.query.get_or_404(etudiant_id)
        nom_etudiant = f"{etudiant.nom} {etudiant.prenom}"
        
        # Supprimer l'utilisateur associé s'il existe
        if etudiant.utilisateur:
            db.session.delete(etudiant.utilisateur)
        
        # Supprimer l'étudiant
        db.session.delete(etudiant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Étudiant "{nom_etudiant}" supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        })

@bp.route('/etudiants/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_etudiant():
    """Créer un nouvel étudiant"""
    from app.forms.academique import FormulaireEtudiant
    
    formulaire = FormulaireEtudiant()
    
    # Remplir les choix d'années académiques
    annees = AnneeAcademique.query.all()
    formulaire.annee_academique_id.choices = [(annee.id, annee.nom) for annee in annees]
    
    if formulaire.validate_on_submit():
        try:
            # Vérifier que le matricule n'existe pas déjà
            if Etudiant.query.filter_by(matricule=formulaire.matricule.data).first():
                flash('Ce matricule existe déjà. Veuillez choisir un autre matricule.', 'error')
                return render_template('admin/creer_etudiant.html', formulaire=formulaire)
            
            # Vérifier que l'email n'existe pas déjà
            if Etudiant.query.filter_by(email=formulaire.email.data).first():
                flash('Cet email existe déjà. Veuillez choisir un autre email.', 'error')
                return render_template('admin/creer_etudiant.html', formulaire=formulaire)
            
            # Créer l'étudiant
            etudiant = Etudiant(
                matricule=formulaire.matricule.data,
                nom=formulaire.nom.data,
                prenom=formulaire.prenom.data,
                date_naissance=formulaire.date_naissance.data,
                sexe=formulaire.sexe.data,
                telephone=formulaire.telephone.data,
                email=formulaire.email.data,
                adresse=formulaire.adresse.data,
                annee_academique_id=formulaire.annee_academique_id.data
            )
            
            # Créer le compte utilisateur
            # Générer un mot de passe par défaut si aucun n'est fourni
            mot_de_passe = formulaire.mot_de_passe.data if formulaire.mot_de_passe.data else 'etudiant123'
            
            utilisateur = Utilisateur(
                nom=formulaire.nom.data,
                prenom=formulaire.prenom.data,
                email=formulaire.email.data,
                mot_de_passe=mot_de_passe,
                role='etudiant',
                actif=True
            )
            
            db.session.add(utilisateur)
            db.session.flush()  # Pour obtenir l'ID de l'utilisateur
            
            # Lier l'étudiant à l'utilisateur
            etudiant.utilisateur_id = utilisateur.id
            
            db.session.add(etudiant)
            db.session.commit()
            
            flash(f'Étudiant "{etudiant.prenom} {etudiant.nom}" créé avec succès !', 'success')
            return redirect(url_for('admin.etudiants'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création de l\'étudiant: {str(e)}', 'error')
    
    return render_template('admin/creer_etudiant.html', formulaire=formulaire)

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
            
            # Créer le compte utilisateur
            utilisateur = Utilisateur(
                nom=formulaire.nom.data,
                prenom=formulaire.prenom.data,
                email=formulaire.email.data,
                mot_de_passe=formulaire.mot_de_passe.data,
                role='enseignant',
                actif=True
            )
            
            db.session.add(utilisateur)
            db.session.flush()  # Pour obtenir l'ID de l'utilisateur
            
            # Lier l'enseignant à l'utilisateur
            enseignant.utilisateur_id = utilisateur.id
            
            db.session.add(enseignant)
            db.session.commit()
            
            flash(f'Enseignant "{enseignant.nom_complet}" créé avec succès ! Compte utilisateur créé avec le mot de passe saisi.', 'success')
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
            
            # Gérer la modification du mot de passe si fourni
            if formulaire.mot_de_passe.data and formulaire.confirmer_mot_de_passe.data:
                if enseignant.utilisateur:
                    from werkzeug.security import generate_password_hash
                    enseignant.utilisateur.mot_de_passe = generate_password_hash(formulaire.mot_de_passe.data)
                    db.session.commit()
                    flash('Mot de passe mis à jour avec succès !', 'success')
            
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

@bp.route('/enseignants/supprimer/<int:enseignant_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_enseignant(enseignant_id):
    """Supprimer un enseignant"""
    from flask import jsonify
    
    try:
        enseignant = Enseignant.query.get_or_404(enseignant_id)
        nom_enseignant = f"{enseignant.nom} {enseignant.prenom}"
        
        # Supprimer l'utilisateur associé s'il existe
        if enseignant.utilisateur:
            db.session.delete(enseignant.utilisateur)
        
        # Supprimer l'enseignant
        db.session.delete(enseignant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Enseignant "{nom_enseignant}" supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        })

# ==================== GESTION DES GROUPES ====================

@bp.route('/groupes')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def groupes():
    """Liste des groupes organisés par semestres et UEs"""
    # Obtenir l'année académique active
    annee_active = ServiceAcademique.obtenir_annee_active()
    
    if not annee_active:
        return render_template('admin/groupes.html', annee_active=None, semestres=[])
    
    # Obtenir tous les semestres avec leurs UEs et groupes
    semestres = Semestre.query.filter_by(annee_academique_id=annee_active.id).order_by(Semestre.nom).all()
    
    # Charger les relations pour éviter les requêtes N+1
    for semestre in semestres:
        for ue in semestre.unites_enseignement:
            # Charger les groupes avec leurs relations
            ue.groupes = Groupe.query.filter_by(unite_enseignement_id=ue.id).all()
            # Les propriétés nombre_etudiants et etudiants sont calculées automatiquement par le modèle
    
    return render_template('admin/groupes.html', annee_active=annee_active, semestres=semestres)

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

@bp.route('/groupes/creer/<int:ue_id>', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_groupe_ue(ue_id):
    """Créer un nouveau groupe pour une UE spécifique"""
    # Vérifier que l'UE existe
    ue = UniteEnseignement.query.get_or_404(ue_id)
    
    formulaire = FormulaireGroupe()
    
    # Pré-remplir l'UE
    formulaire.unite_enseignement_id.data = ue_id
    
    # Remplir les choix d'unités d'enseignement (pour la validation)
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
            ue_id=ue_id,  # Utiliser l'UE pré-définie
            enseignant_id=formulaire.enseignant_responsable_id.data if formulaire.enseignant_responsable_id.data else None,
            description=formulaire.description.data
        )
        
        if succes:
            flash(f'Groupe "{groupe.code}" créé avec succès pour l\'UE {ue.code} !', 'success')
            return redirect(url_for('admin.groupes'))
        else:
            flash('Erreur lors de la création du groupe.', 'error')
    
    return render_template('admin/creer_groupe.html', 
                         formulaire=formulaire, 
                         annee_active=ServiceAcademique.obtenir_annee_active(),
                         ue_predefinie=ue)

@bp.route('/groupes/<int:groupe_id>/supprimer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_groupe(groupe_id):
    """Supprimer un groupe"""
    from flask import jsonify, request
    
    try:
        groupe = Groupe.query.get_or_404(groupe_id)
        nom_groupe = f"{groupe.code} - {groupe.nom}"
        
        # Vérifier s'il y a des étudiants inscrits
        if groupe.nombre_etudiants > 0:
            return jsonify({
                'success': False,
                'message': f'Impossible de supprimer le groupe "{nom_groupe}" car il contient {groupe.nombre_etudiants} étudiant(s) inscrit(s).'
            })
        
        # Supprimer le groupe
        db.session.delete(groupe)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Groupe "{nom_groupe}" supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        })

@bp.route('/groupes/<int:groupe_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_groupe(groupe_id):
    """Modifier un groupe existant"""
    groupe = Groupe.query.get_or_404(groupe_id)
    formulaire = FormulaireGroupe(obj=groupe)
    
    # Remplir les choix d'unités d'enseignement
    ues = ServiceAcademique.obtenir_toutes_unites_enseignement()
    formulaire.unite_enseignement_id.choices = [(ue.id, f"{ue.code} - {ue.nom}") for ue in ues]
    
    # Remplir les choix d'enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    formulaire.enseignant_responsable_id.choices = [('', '-- Sélectionner un enseignant --')] + [(e.id, f"{e.nom_complet} ({e.matricule})") for e in enseignants]
    
    if formulaire.validate_on_submit():
        try:
            # Mettre à jour les informations du groupe
            groupe.nom = formulaire.nom.data
            groupe.code = formulaire.code.data
            groupe.capacite_max = formulaire.capacite_max.data
            groupe.unite_enseignement_id = formulaire.unite_enseignement_id.data
            groupe.enseignant_responsable_id = formulaire.enseignant_responsable_id.data if formulaire.enseignant_responsable_id.data else None
            groupe.description = formulaire.description.data
            
            db.session.commit()
            flash(f'Groupe "{groupe.code}" modifié avec succès !', 'success')
            return redirect(url_for('admin.groupes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('admin/modifier_groupe.html', formulaire=formulaire, groupe=groupe)

@bp.route('/groupes/<int:groupe_id>/details')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def details_groupe(groupe_id):
    """Afficher les détails d'un groupe"""
    groupe = Groupe.query.get_or_404(groupe_id)
    
    # Obtenir les statistiques du groupe
    nombre_etudiants = groupe.nombre_etudiants
    taux_remplissage = (nombre_etudiants / groupe.capacite_max * 100) if groupe.capacite_max > 0 else 0
    
    # Obtenir les notes moyennes du groupe si disponibles
    notes_groupe = Note.query.filter_by(groupe_id=groupe.id).all()
    moyenne_groupe = sum(note.moyenne for note in notes_groupe) / len(notes_groupe) if notes_groupe else None
    
    return render_template('admin/details_groupe.html', 
                         groupe=groupe, 
                         nombre_etudiants=nombre_etudiants,
                         taux_remplissage=taux_remplissage,
                         moyenne_groupe=moyenne_groupe)

@bp.route('/groupes/<int:groupe_id>/gestion-inscriptions')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def gestion_inscriptions_groupe(groupe_id):
    """Gérer les inscriptions d'un groupe"""
    groupe = Groupe.query.get_or_404(groupe_id)
    
    # Obtenir tous les étudiants disponibles pour l'inscription
    etudiants_disponibles = Etudiant.query.filter(
        ~Etudiant.inscriptions_groupes.any(InscriptionGroupe.groupe_id == groupe_id)
    ).all()
    
    # Obtenir les étudiants déjà inscrits
    etudiants_inscrits = groupe.etudiants
    
    return render_template('admin/gestion_inscriptions_groupe.html', 
                         groupe=groupe,
                         etudiants_disponibles=etudiants_disponibles,
                         etudiants_inscrits=etudiants_inscrits)

@bp.route('/groupes/<int:groupe_id>/inscrire-etudiant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def inscrire_etudiant_groupe(groupe_id):
    """Inscrire un étudiant dans un groupe"""
    from flask import jsonify, request
    
    try:
        data = request.get_json()
        etudiant_id = data.get('etudiant_id')
        
        if not etudiant_id:
            return jsonify({'success': False, 'message': 'ID étudiant manquant'})
        
        groupe = Groupe.query.get_or_404(groupe_id)
        etudiant = Etudiant.query.get_or_404(etudiant_id)
        
        # Vérifier si l'étudiant est déjà inscrit
        inscription_existante = InscriptionGroupe.query.filter_by(
            etudiant_id=etudiant_id, 
            groupe_id=groupe_id
        ).first()
        
        if inscription_existante:
            return jsonify({'success': False, 'message': f'L\'étudiant {etudiant.nom_complet} est déjà inscrit dans ce groupe'})
        
        # Vérifier la capacité du groupe
        if groupe.nombre_etudiants >= groupe.capacite_max:
            return jsonify({'success': False, 'message': f'Le groupe est plein (capacité: {groupe.capacite_max})'})
        
        # Créer l'inscription
        nouvelle_inscription = InscriptionGroupe(
            etudiant_id=etudiant_id,
            groupe_id=groupe_id
        )
        db.session.add(nouvelle_inscription)
        db.session.commit()
        
        # Calculer les nouvelles statistiques
        nouveau_nombre_etudiants = len(groupe.etudiants)
        nouveau_taux_remplissage = (nouveau_nombre_etudiants / groupe.capacite_max * 100) if groupe.capacite_max > 0 else 0
        nouveau_places_disponibles = groupe.capacite_max - nouveau_nombre_etudiants
        
        return jsonify({
            'success': True, 
            'message': f'Étudiant {etudiant.nom_complet} inscrit avec succès dans le groupe {groupe.code}',
            'nouveau_nombre_etudiants': nouveau_nombre_etudiants,
            'nouveau_taux_remplissage': round(nouveau_taux_remplissage, 1),
            'nouveau_places_disponibles': nouveau_places_disponibles,
            'etudiant': {
                'id': etudiant.id,
                'matricule': etudiant.matricule,
                'nom': etudiant.nom,
                'prenom': etudiant.prenom
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de l\'inscription: {str(e)}'})

@bp.route('/groupes/<int:groupe_id>/desinscrire-etudiant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def desinscrire_etudiant_groupe(groupe_id):
    """Désinscrire un étudiant d'un groupe"""
    from flask import jsonify, request
    
    try:
        data = request.get_json()
        etudiant_id = data.get('etudiant_id')
        
        if not etudiant_id:
            return jsonify({'success': False, 'message': 'ID étudiant manquant'})
        
        groupe = Groupe.query.get_or_404(groupe_id)
        etudiant = Etudiant.query.get_or_404(etudiant_id)
        
        # Vérifier si l'étudiant est inscrit
        inscription_existante = InscriptionGroupe.query.filter_by(
            etudiant_id=etudiant_id, 
            groupe_id=groupe_id
        ).first()
        
        if not inscription_existante:
            return jsonify({'success': False, 'message': f'L\'étudiant {etudiant.nom_complet} n\'est pas inscrit dans ce groupe'})
        
        # Supprimer l'inscription
        db.session.delete(inscription_existante)
        db.session.commit()
        
        # Calculer les nouvelles statistiques
        nouveau_nombre_etudiants = len(groupe.etudiants)
        nouveau_taux_remplissage = (nouveau_nombre_etudiants / groupe.capacite_max * 100) if groupe.capacite_max > 0 else 0
        nouveau_places_disponibles = groupe.capacite_max - nouveau_nombre_etudiants
        
        return jsonify({
            'success': True, 
            'message': f'Étudiant {etudiant.nom_complet} désinscrit avec succès du groupe {groupe.code}',
            'nouveau_nombre_etudiants': nouveau_nombre_etudiants,
            'nouveau_taux_remplissage': round(nouveau_taux_remplissage, 1),
            'nouveau_places_disponibles': nouveau_places_disponibles,
            'etudiant': {
                'id': etudiant.id,
                'matricule': etudiant.matricule,
                'nom': etudiant.nom,
                'prenom': etudiant.prenom
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la désinscription: {str(e)}'})

# ==================== GESTION DES NOTIFICATIONS ====================

@bp.route('/notifications')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def notifications():
    """Liste des notifications"""
    notifications = ServiceNotification.get_all_notifications()
    return render_template('admin/notifications/liste.html', notifications=notifications)

@bp.route('/notifications/<int:notification_id>/marquer-lue')
@login_required
@utilisateur_actif_requis
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
@utilisateur_actif_requis
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
@utilisateur_actif_requis
@administrateur_requis
def envoyer_notification():
    """Envoyer une notification"""
    from app.forms.notification import FormulaireNotification
    from app.models.academique import Groupe
    
    formulaire = FormulaireNotification()
    
    # Charger les groupes pour le formulaire
    formulaire.groupe_id.choices = [(0, 'Sélectionner un groupe')] + [(g.id, g.nom) for g in Groupe.query.all()]
    
    if formulaire.validate_on_submit():
        try:
            # Gérer l'envoi selon le type de destinataire
            if formulaire.destinataires.data == 'groupe' and formulaire.groupe_id.data:
                # Notification pour un groupe spécifique
                success = ServiceNotification.creer_notification_groupe(
                    groupe_id=formulaire.groupe_id.data,
                    titre=formulaire.titre.data,
                    message=formulaire.contenu.data,
                    envoyer_email=formulaire.envoyer_email.data
                )
            else:
                # Notification pour tous, étudiants, enseignants ou admins
                success = ServiceNotification.creer_notification_avancee(
                    titre=formulaire.titre.data,
                    contenu=formulaire.contenu.data,
                    type_notification=formulaire.type_notification.data,
                    destinataires=formulaire.destinataires.data,
                    expediteur_id=current_user.id,
                    envoyer_email=formulaire.envoyer_email.data
                )
            
            if success:
                flash('Notification envoyée avec succès !', 'success')
            else:
                flash('Erreur lors de l\'envoi de la notification', 'error')
                
            return redirect(url_for('admin.notifications'))
            
        except Exception as e:
            flash(f'Erreur lors de l\'envoi: {str(e)}', 'error')
    
    return render_template('admin/notifications/envoyer.html', formulaire=formulaire)

# ==================== GESTION PÉDAGOGIQUE ====================

@bp.route('/pedagogique/validation-notes')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def validation_notes():
    """Page de validation des notes par les administrateurs"""
    from app.models.pedagogique import Note
    from app.models.academique import Matiere, Groupe, Semestre
    
    # Filtres
    matiere_id = request.args.get('matiere_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    statut = request.args.get('statut', 'non_validees')  # non_validees, validees, toutes
    
    # Construire la requête
    query = Note.query
    
    if matiere_id:
        query = query.filter_by(matiere_id=matiere_id)
    if groupe_id:
        query = query.filter_by(groupe_id=groupe_id)
    if semestre_id:
        query = query.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
    
    if statut == 'non_validees':
        query = query.filter_by(validee=False)
    elif statut == 'validees':
        query = query.filter_by(validee=True)
    
    notes = query.order_by(Note.date_saisie.desc()).all()
    
    # Options pour les filtres
    matieres = Matiere.query.all()
    groupes = Groupe.query.all()
    semestres = Semestre.query.all()
    
    return render_template('admin/pedagogique/validation_notes.html',
                         notes=notes,
                         matieres=matieres,
                         groupes=groupes,
                         semestres=semestres)

@bp.route('/pedagogique/valider-note/<int:note_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def valider_note(note_id):
    """Valider une note spécifique"""
    from app.models.pedagogique import Note
    
    note = Note.query.get_or_404(note_id)
    commentaire = request.form.get('commentaire', '')
    
    note.validee = True
    note.validee_par = current_user.id
    note.date_validation = datetime.utcnow()
    note.commentaire_validation = commentaire
    
    db.session.commit()
    
    flash('Note validée avec succès', 'success')
    return redirect(url_for('admin.validation_notes'))

@bp.route('/pedagogique/invalider-note/<int:note_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def invalider_note(note_id):
    """Invalider une note validée"""
    from app.models.pedagogique import Note
    
    note = Note.query.get_or_404(note_id)
    
    note.validee = False
    note.validee_par = None
    note.date_validation = None
    note.commentaire_validation = None
    
    db.session.commit()
    
    flash('Note invalidée avec succès', 'success')
    return redirect(url_for('admin.validation_notes'))

@bp.route('/pedagogique/deliberations')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def deliberations():
    """Gestion des délibérations"""
    from app.models.pedagogique import Deliberation
    from app.models.academique import Semestre, Groupe
    
    # Filtres
    semestre_id = request.args.get('semestre_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    
    query = Deliberation.query
    
    if semestre_id:
        query = query.filter_by(semestre_id=semestre_id)
    if groupe_id:
        query = query.filter_by(groupe_id=groupe_id)
    
    deliberations = query.order_by(Deliberation.date_deliberation.desc()).all()
    
    # Options pour les filtres
    semestres = Semestre.query.all()
    groupes = Groupe.query.all()
    
    return render_template('admin/pedagogique/deliberations.html',
                         deliberations=deliberations,
                         semestres=semestres,
                         groupes=groupes)

@bp.route('/pedagogique/creer-deliberation', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_deliberation():
    """Créer une nouvelle délibération"""
    from app.models.pedagogique import Deliberation
    from app.models.academique import Semestre, Groupe
    
    if request.method == 'POST':
        semestre_id = request.form.get('semestre_id', type=int)
        groupe_id = request.form.get('groupe_id', type=int)
        commentaire = request.form.get('commentaire', '')
        
        deliberation = Deliberation(
            semestre_id=semestre_id,
            groupe_id=groupe_id,
            commentaire=commentaire,
            date_deliberation=date.today()
        )
        
        db.session.add(deliberation)
        db.session.commit()
        
        flash('Délibération créée avec succès', 'success')
        return redirect(url_for('admin.deliberations'))
    
    semestres = Semestre.query.all()
    groupes = Groupe.query.all()
    
    return render_template('admin/pedagogique/creer_deliberation.html',
                         semestres=semestres,
                         groupes=groupes)

@bp.route('/pedagogique/valider-deliberation/<int:deliberation_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def valider_deliberation(deliberation_id):
    """Valider une délibération"""
    from app.models.pedagogique import Deliberation
    
    deliberation = Deliberation.query.get_or_404(deliberation_id)
    
    deliberation.statut = Deliberation.STATUT_VALIDEE
    deliberation.date_validation = date.today()
    
    db.session.commit()
    
    flash('Délibération validée avec succès', 'success')
    return redirect(url_for('admin.detail_deliberation', deliberation_id=deliberation_id))

@bp.route('/pedagogique/detail-deliberation/<int:deliberation_id>')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def detail_deliberation(deliberation_id):
    """Détail d'une délibération"""
    from app.models.pedagogique import Deliberation
    
    deliberation = Deliberation.query.get_or_404(deliberation_id)
    
    return render_template('admin/pedagogique/detail_deliberation.html',
                         deliberation=deliberation)

# ==================== RAPPORTS ====================

@bp.route('/rapports/performance')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def rapports_performance():
    """Rapports de performance par classe/département"""
    from app.models.pedagogique import Note
    from app.models.academique import Groupe, Matiere, Semestre
    
    # Filtres
    semestre_id = request.args.get('semestre_id', type=int)
    groupe_id = request.args.get('groupe_id', type=int)
    
    # Statistiques générales
    total_notes = Note.query.count()
    moyenne_generale = db.session.query(func.avg(Note.note)).scalar() or 0
    
    # Performance par groupe
    query_groupes = db.session.query(
        Groupe.nom,
        func.count(Note.id).label('total_notes'),
        func.avg(Note.note).label('moyenne'),
        func.count(case([(Note.note >= 10, 1)])).label('notes_validees')
    ).join(Note).group_by(Groupe.id, Groupe.nom)
    
    if semestre_id:
        query_groupes = query_groupes.join(Matiere).join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
    
    if groupe_id:
        query_groupes = query_groupes.filter(Groupe.id == groupe_id)
    
    performance_groupes = query_groupes.all()
    
    # Performance par matière
    query_matieres = db.session.query(
        Matiere.nom,
        func.count(Note.id).label('total_notes'),
        func.avg(Note.note).label('moyenne'),
        func.count(case([(Note.note >= 10, 1)])).label('notes_validees')
    ).join(Note).group_by(Matiere.id, Matiere.nom)
    
    if semestre_id:
        query_matieres = query_matieres.join(UniteEnseignement).filter(UniteEnseignement.semestre_id == semestre_id)
    
    performance_matieres = query_matieres.all()
    
    # Options pour les filtres
    semestres = Semestre.query.all()
    groupes = Groupe.query.all()
    
    return render_template('admin/rapports/performance.html',
                         total_notes=total_notes,
                         moyenne_generale=moyenne_generale,
                         performance_groupes=performance_groupes,
                         performance_matieres=performance_matieres,
                         semestres=semestres,
                         groupes=groupes)

@bp.route('/rapports/statistiques-avancees')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def statistiques_avancees():
    """Statistiques avancées avec graphiques"""
    from app.models.pedagogique import Note, Absence
    from app.models.academique import Etudiant, Groupe, Semestre
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    
    # Évolution des moyennes par mois
    evolution_moyennes = db.session.query(
        extract('month', Note.date_saisie).label('mois'),
        func.avg(Note.note).label('moyenne')
    ).group_by(extract('month', Note.date_saisie)).order_by('mois').all()
    
    # Taux de réussite par groupe
    taux_reussite = db.session.query(
        Groupe.nom,
        func.count(Note.id).label('total'),
        func.count(case([(Note.note >= 10, 1)])).label('reussites')
    ).join(Note).group_by(Groupe.id, Groupe.nom).all()
    
    # Statistiques des absences
    total_absences = Absence.query.count()
    absences_justifiees = Absence.query.filter_by(justifiee=True).count()
    taux_justification = (absences_justifiees / total_absences * 100) if total_absences > 0 else 0
    
    # Répartition des notes
    repartition_notes = {
        'excellent': Note.query.filter(Note.note >= 16).count(),
        'tres_bien': Note.query.filter(Note.note >= 14, Note.note < 16).count(),
        'bien': Note.query.filter(Note.note >= 12, Note.note < 14).count(),
        'assez_bien': Note.query.filter(Note.note >= 10, Note.note < 12).count(),
        'insuffisant': Note.query.filter(Note.note < 10).count()
    }
    
    # Options pour les filtres
    semestres = Semestre.query.all()
    
    return render_template('admin/rapports/statistiques_avancees.html',
                         evolution_moyennes=evolution_moyennes,
                         taux_reussite=taux_reussite,
                         total_absences=total_absences,
                         absences_justifiees=absences_justifiees,
                         taux_justification=taux_justification,
                         repartition_notes=repartition_notes,
                         semestres=semestres)

# ==================== FRAIS DE SCOLARITÉ ====================

@bp.route('/frais-scolarite')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def frais_scolarite():
    """Gestion des frais de scolarité"""
    from app.models.academique import Etudiant, AnneeAcademique
    from datetime import datetime, timedelta
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    statut = request.args.get('statut', 'tous')  # tous, payes, impayes
    
    # Récupérer les étudiants avec leurs frais
    query = Etudiant.query
    
    if annee_id:
        query = query.filter_by(annee_academique_id=annee_id)
    
    etudiants = query.all()
    
    # Simuler les frais de scolarité (à remplacer par un vrai modèle)
    frais_etudiants = []
    for etudiant in etudiants:
        frais = {
            'etudiant': etudiant,
            'montant_total': 50000,  # FCFA
            'montant_paye': 35000 if etudiant.id % 3 != 0 else 50000,  # Simulation
            'date_limite': datetime.now() + timedelta(days=30),
            'statut': 'paye' if etudiant.id % 3 != 0 else 'impaye'
        }
        frais['reste'] = frais['montant_total'] - frais['montant_paye']
        frais_etudiants.append(frais)
    
    # Filtrer par statut
    if statut == 'payes':
        frais_etudiants = [f for f in frais_etudiants if f['statut'] == 'paye']
    elif statut == 'impayes':
        frais_etudiants = [f for f in frais_etudiants if f['statut'] == 'impaye']
    
    # Options pour les filtres
    annees = AnneeAcademique.query.all()
    
    return render_template('admin/frais_scolarite.html',
                         frais_etudiants=frais_etudiants,
                         annees=annees)

@bp.route('/frais-scolarite/etudiant/<int:etudiant_id>')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def detail_frais_etudiant(etudiant_id):
    """Détail des frais de scolarité d'un étudiant"""
    from app.models.academique import Etudiant
    from datetime import datetime, timedelta
    
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    
    # Simuler l'historique des paiements
    historique_paiements = [
        {
            'date': datetime.now() - timedelta(days=30),
            'montant': 20000,
            'mode': 'Virement bancaire',
            'reference': 'VIR-2024-001'
        },
        {
            'date': datetime.now() - timedelta(days=15),
            'montant': 15000,
            'mode': 'Espèces',
            'reference': 'ESP-2024-002'
        }
    ]
    
    return render_template('admin/detail_frais_etudiant.html',
                         etudiant=etudiant,
                         historique_paiements=historique_paiements)

@bp.route('/frais-scolarite/enregistrer-paiement/<int:etudiant_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def enregistrer_paiement(etudiant_id):
    """Enregistrer un nouveau paiement"""
    from app.models.academique import Etudiant
    
    etudiant = Etudiant.query.get_or_404(etudiant_id)
    
    montant = request.form.get('montant', type=float)
    mode_paiement = request.form.get('mode_paiement', '')
    reference = request.form.get('reference', '')
    
    if not montant or montant <= 0:
        flash('Montant invalide', 'error')
        return redirect(url_for('admin.detail_frais_etudiant', etudiant_id=etudiant_id))
    
    # Ici on enregistrerait le paiement dans la base de données
    # Pour l'instant, on simule
    
    flash(f'Paiement de {montant} FCFA enregistré avec succès', 'success')
    return redirect(url_for('admin.detail_frais_etudiant', etudiant_id=etudiant_id))

# ==================== PROFIL ADMIN ====================

@bp.route('/profil')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def profil():
    """Profil de l'administrateur connecté"""
    # Récupérer les statistiques pour l'affichage
    stats = ServiceAcademique.obtenir_statistiques_generales()
    return render_template('admin/profil.html', utilisateur=current_user, stats=stats)

# ==================== DASHBOARD PÉDAGOGIQUE ====================

@bp.route('/pedagogique')
@login_required
@utilisateur_actif_requis
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
@utilisateur_actif_requis
@administrateur_requis
def pedagogique_dashboard_redirect():
    """Redirection vers le dashboard pédagogique"""
    return redirect(url_for('admin.pedagogique_dashboard'))

@bp.route('/pedagogique/rapports')
@login_required
@utilisateur_actif_requis
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

# ==================== RAPPORTS DÉTAILLÉS ====================

@bp.route('/rapport-performance')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def rapport_performance():
    """Rapport de performance des étudiants"""
    from app.models.academique import Etudiant, Groupe, UniteEnseignement
    from app.models.pedagogique import Note
    
    # Statistiques de performance
    total_etudiants = Etudiant.query.count()
    total_notes = Note.query.count()
    
    # Moyenne générale (simulation)
    moyenne_generale = 14.5
    
    # Performance par groupe (simulation)
    groupes_performance = []
    groupes = Groupe.query.all()
    for groupe in groupes:
        performance = {
            'groupe': groupe,
            'moyenne': 12.5 + (groupe.id % 5),  # Simulation
            'etudiants': groupe.etudiants.count() if groupe.etudiants else 0
        }
        groupes_performance.append(performance)
    
    return render_template('admin/rapports/performance.html',
                         total_etudiants=total_etudiants,
                         total_notes=total_notes,
                         moyenne_generale=moyenne_generale,
                         groupes_performance=groupes_performance)

@bp.route('/rapport-assiduite')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def rapport_assiduite():
    """Rapport d'assiduité des étudiants"""
    from app.models.academique import Etudiant, Groupe
    from app.models.pedagogique import Absence
    
    # Statistiques d'assiduité
    total_etudiants = Etudiant.query.count()
    total_absences = Absence.query.count()
    
    # Taux de présence (simulation)
    taux_presence = 85.5
    
    # Assiduité par groupe (simulation)
    groupes_assiduite = []
    groupes = Groupe.query.all()
    for groupe in groupes:
        assiduite = {
            'groupe': groupe,
            'taux_presence': 80 + (groupe.id % 15),  # Simulation
            'absences': groupe.id * 2,  # Simulation
            'etudiants': groupe.etudiants.count() if groupe.etudiants else 0
        }
        groupes_assiduite.append(assiduite)
    
    return render_template('admin/rapports/assiduite.html',
                         total_etudiants=total_etudiants,
                         total_absences=total_absences,
                         taux_presence=taux_presence,
                         groupes_assiduite=groupes_assiduite)

@bp.route('/rapport-pedagogique')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def rapport_pedagogique():
    """Rapport pédagogique général"""
    from app.models.academique import Etudiant, Enseignant, Groupe, UniteEnseignement
    from app.models.pedagogique import Note, Absence
    
    # Statistiques générales
    total_etudiants = Etudiant.query.count()
    total_enseignants = Enseignant.query.count()
    total_groupes = Groupe.query.count()
    total_ues = UniteEnseignement.query.count()
    total_notes = Note.query.count()
    total_absences = Absence.query.count()
    
    # Répartition par sexe
    etudiants_hommes = Etudiant.query.filter_by(sexe='M').count()
    etudiants_femmes = Etudiant.query.filter_by(sexe='F').count()
    
    # Activité récente (simulation)
    activite_recente = {
        'notes_saisies': 150,
        'absences_enregistrees': 25,
        'groupes_crees': 3,
        'etudiants_inscrits': 12
    }
    
    return render_template('admin/rapports/pedagogique.html',
                         total_etudiants=total_etudiants,
                         total_enseignants=total_enseignants,
                         total_groupes=total_groupes,
                         total_ues=total_ues,
                         total_notes=total_notes,
                         total_absences=total_absences,
                         etudiants_hommes=etudiants_hommes,
                         etudiants_femmes=etudiants_femmes,
                         activite_recente=activite_recente)

# ==================== GESTION DU PROFIL ====================

@bp.route('/modifier-profil', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_profil():
    """Modifier les informations du profil"""
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    telephone = request.form.get('telephone')
    
    if not nom or not prenom or not email:
        flash('Tous les champs obligatoires doivent être remplis', 'error')
        return redirect(url_for('admin.profil'))
    
    # Mettre à jour les informations
    current_user.nom = nom
    current_user.prenom = prenom
    current_user.email = email
    current_user.telephone = telephone
    
    try:
        db.session.commit()
        flash('Profil mis à jour avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la mise à jour du profil', 'error')
    
    return redirect(url_for('admin.profil'))

@bp.route('/changer-mot-de-passe', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def changer_mot_de_passe():
    """Changer le mot de passe"""
    from werkzeug.security import check_password_hash, generate_password_hash
    
    ancien_mdp = request.form.get('ancien_mdp')
    nouveau_mdp = request.form.get('nouveau_mdp')
    confirmer_mdp = request.form.get('confirmer_mdp')
    
    if not ancien_mdp or not nouveau_mdp or not confirmer_mdp:
        flash('Tous les champs doivent être remplis', 'error')
        return redirect(url_for('admin.profil'))
    
    if nouveau_mdp != confirmer_mdp:
        flash('Les nouveaux mots de passe ne correspondent pas', 'error')
        return redirect(url_for('admin.profil'))
    
    if not check_password_hash(current_user.mot_de_passe, ancien_mdp):
        flash('Ancien mot de passe incorrect', 'error')
        return redirect(url_for('admin.profil'))
    
    # Mettre à jour le mot de passe
    current_user.mot_de_passe = generate_password_hash(nouveau_mdp)
    
    try:
        db.session.commit()
        flash('Mot de passe changé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors du changement de mot de passe', 'error')
    
    return redirect(url_for('admin.profil'))

# ==================== ROUTES POUR GROUPES GÉNÉRIQUES ====================

@bp.route('/groupes-generiques')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def groupes_generiques():
    """Liste des groupes génériques"""
    groupes = ServiceAcademique.obtenir_tous_groupes_generiques()
    return render_template('admin/groupes_generiques.html', groupes=groupes)

@bp.route('/groupes-generiques/creer', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_groupe_generique():
    """Créer un nouveau groupe générique"""
    form = FormulaireGroupeGenerique()
    
    # Remplir les choix pour les enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    form.enseignant_responsable_id.choices = [('', 'Aucun enseignant')] + [(e.id, f"{e.nom} {e.prenom}") for e in enseignants]
    
    if form.validate_on_submit():
        groupe, success = ServiceAcademique.creer_groupe_generique(
            nom=form.nom.data,
            code=form.code.data,
            capacite_max=form.capacite_max.data,
            enseignant_id=form.enseignant_responsable_id.data if form.enseignant_responsable_id.data else None,
            description=form.description.data
        )
        
        if success:
            flash('Groupe générique créé avec succès!', 'success')
            return redirect(url_for('admin.groupes_generiques'))
        else:
            flash('Erreur lors de la création du groupe générique.', 'error')
    
    return render_template('admin/creer_groupe_generique.html', form=form)

@bp.route('/groupes-generiques/<int:groupe_id>/modifier', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def modifier_groupe_generique(groupe_id):
    """Modifier un groupe générique"""
    groupe = ServiceAcademique.obtenir_groupe_generique_par_id(groupe_id)
    if not groupe:
        flash('Groupe générique non trouvé.', 'error')
        return redirect(url_for('admin.groupes_generiques'))
    
    form = FormulaireGroupeGenerique(obj=groupe)
    
    # Remplir les choix pour les enseignants
    enseignants = ServiceAcademique.obtenir_tous_enseignants()
    form.enseignant_responsable_id.choices = [('', 'Aucun enseignant')] + [(e.id, f"{e.nom} {e.prenom}") for e in enseignants]
    
    if form.validate_on_submit():
        success = ServiceAcademique.modifier_groupe_generique(
            groupe_id=groupe_id,
            nom=form.nom.data,
            code=form.code.data,
            capacite_max=form.capacite_max.data,
            enseignant_id=form.enseignant_responsable_id.data if form.enseignant_responsable_id.data else None,
            description=form.description.data
        )
        
        if success:
            flash('Groupe générique modifié avec succès!', 'success')
            return redirect(url_for('admin.groupes_generiques'))
        else:
            flash('Erreur lors de la modification du groupe générique.', 'error')
    
    return render_template('admin/modifier_groupe_generique.html', form=form, groupe=groupe)

@bp.route('/groupes-generiques/<int:groupe_id>/details')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def details_groupe_generique(groupe_id):
    """Détails d'un groupe générique"""
    groupe = ServiceAcademique.obtenir_groupe_generique_par_id(groupe_id)
    if not groupe:
        flash('Groupe générique non trouvé.', 'error')
        return redirect(url_for('admin.groupes_generiques'))
    
    etudiants = ServiceAcademique.obtenir_etudiants_groupe_generique(groupe_id)
    ues_liees = ServiceAcademique.obtenir_ues_par_groupe_generique(groupe_id)
    
    return render_template('admin/details_groupe_generique.html', 
                         groupe=groupe, 
                         etudiants=etudiants, 
                         ues_liees=ues_liees)

@bp.route('/groupes-generiques/<int:groupe_id>/supprimer', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def supprimer_groupe_generique(groupe_id):
    """Supprimer un groupe générique"""
    from app.models.academique import GroupeGenerique
    
    groupe = GroupeGenerique.query.get(groupe_id)
    if not groupe:
        flash('Groupe générique non trouvé.', 'error')
        return redirect(url_for('admin.groupes_generiques'))
    
    try:
        # Vérifier s'il y a des inscriptions
        if groupe.inscriptions_generiques:
            flash('Impossible de supprimer ce groupe car il contient des étudiants inscrits.', 'error')
            return redirect(url_for('admin.groupes_generiques'))
        
        # Vérifier s'il y a des utilisations avec des UE
        if groupe.utilisations_ue:
            flash('Impossible de supprimer ce groupe car il est utilisé par des UE.', 'error')
            return redirect(url_for('admin.groupes_generiques'))
        
        db.session.delete(groupe)
        db.session.commit()
        flash('Groupe générique supprimé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression du groupe générique.', 'error')
    
    return redirect(url_for('admin.groupes_generiques'))

@bp.route('/groupes-generiques/creer-automatiquement', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def creer_groupes_generiques_automatiquement():
    """Créer automatiquement des groupes génériques"""
    nombre_groupes = request.form.get('nombre_groupes', 3, type=int)
    capacite_max = request.form.get('capacite_max', 30, type=int)
    
    groupes_crees = ServiceAcademique.creer_groupes_generiques_automatiques(
        nombre_groupes=nombre_groupes,
        capacite_max=capacite_max
    )
    
    if groupes_crees:
        flash(f'{len(groupes_crees)} groupes génériques créés automatiquement!', 'success')
    else:
        flash('Aucun nouveau groupe générique créé.', 'info')
    
    return redirect(url_for('admin.groupes_generiques'))

@bp.route('/groupes-generiques/<int:groupe_id>/lier-ue', methods=['GET', 'POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def lier_groupe_generique_ue(groupe_id):
    """Lier un groupe générique à une UE"""
    groupe = ServiceAcademique.obtenir_groupe_generique_par_id(groupe_id)
    if not groupe:
        flash('Groupe générique non trouvé.', 'error')
        return redirect(url_for('admin.groupes_generiques'))
    
    form = FormulaireUtilisationGroupeUE()
    
    # Remplir les choix
    groupes_generiques = ServiceAcademique.obtenir_tous_groupes_generiques()
    ues = ServiceAcademique.obtenir_toutes_unites_enseignement()
    
    form.groupe_generique_id.choices = [(g.id, f"{g.code} - {g.nom}") for g in groupes_generiques]
    form.unite_enseignement_id.choices = [(ue.id, f"{ue.code} - {ue.nom}") for ue in ues]
    
    # Pré-remplir le groupe sélectionné
    form.groupe_generique_id.data = groupe_id
    
    if form.validate_on_submit():
        success = ServiceAcademique.lier_groupe_generique_ue(
            groupe_generique_id=form.groupe_generique_id.data,
            unite_enseignement_id=form.unite_enseignement_id.data
        )
        
        if success:
            flash('Groupe générique lié à l\'UE avec succès!', 'success')
            return redirect(url_for('admin.details_groupe_generique', groupe_id=groupe_id))
        else:
            flash('Erreur lors de la liaison du groupe à l\'UE.', 'error')
    
    return render_template('admin/lier_groupe_generique_ue.html', form=form, groupe=groupe)

@bp.route('/groupes-generiques/<int:groupe_id>/delier-ue/<int:ue_id>', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def delier_groupe_generique_ue(groupe_id, ue_id):
    """Délier un groupe générique d'une UE"""
    success = ServiceAcademique.delier_groupe_generique_ue(
        groupe_generique_id=groupe_id,
        unite_enseignement_id=ue_id
    )
    
    if success:
        flash('Groupe générique délié de l\'UE avec succès!', 'success')
    else:
        flash('Erreur lors du déliage du groupe de l\'UE.', 'error')
    
    return redirect(url_for('admin.details_groupe_generique', groupe_id=groupe_id))

# ==================== GESTION DES INSCRIPTIONS DES GROUPES GÉNÉRIQUES ====================

@bp.route('/groupes-generiques/<int:groupe_id>/gestion-inscriptions')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def gestion_inscriptions_groupe_generique(groupe_id):
    """Gérer les inscriptions d'un groupe générique"""
    from app.models.academique import GroupeGenerique, InscriptionGroupeGenerique
    
    groupe = GroupeGenerique.query.get_or_404(groupe_id)
    
    # Obtenir tous les étudiants disponibles pour l'inscription
    etudiants_disponibles = Etudiant.query.filter(
        ~Etudiant.inscriptions_groupes_generiques.any(InscriptionGroupeGenerique.groupe_generique_id == groupe_id)
    ).all()
    
    # Obtenir les étudiants déjà inscrits
    etudiants_inscrits = groupe.etudiants
    
    return render_template('admin/gestion_inscriptions_groupe_generique.html', 
                         groupe=groupe,
                         etudiants_disponibles=etudiants_disponibles,
                         etudiants_inscrits=etudiants_inscrits)

@bp.route('/groupes-generiques/<int:groupe_id>/inscrire-etudiant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def inscrire_etudiant_groupe_generique(groupe_id):
    """Inscrire un étudiant dans un groupe générique"""
    from flask import jsonify, request
    from app.models.academique import GroupeGenerique, InscriptionGroupeGenerique
    
    try:
        data = request.get_json()
        etudiant_id = data.get('etudiant_id')
        
        if not etudiant_id:
            return jsonify({'success': False, 'message': 'ID étudiant manquant'})
        
        groupe = GroupeGenerique.query.get_or_404(groupe_id)
        etudiant = Etudiant.query.get_or_404(etudiant_id)
        
        # Vérifier si l'étudiant est déjà inscrit
        inscription_existante = InscriptionGroupeGenerique.query.filter_by(
            etudiant_id=etudiant_id, 
            groupe_generique_id=groupe_id
        ).first()
        
        if inscription_existante:
            return jsonify({'success': False, 'message': f'L\'étudiant {etudiant.nom_complet} est déjà inscrit dans ce groupe générique'})
        
        # Vérifier la capacité du groupe
        if groupe.nombre_etudiants >= groupe.capacite_max:
            return jsonify({'success': False, 'message': f'Le groupe générique est plein (capacité: {groupe.capacite_max})'})
        
        # Créer l'inscription
        nouvelle_inscription = InscriptionGroupeGenerique(
            etudiant_id=etudiant_id,
            groupe_generique_id=groupe_id
        )
        db.session.add(nouvelle_inscription)
        db.session.commit()
        
        # Calculer les nouvelles statistiques
        nouveau_nombre_etudiants = len(groupe.etudiants)
        nouveau_taux_remplissage = (nouveau_nombre_etudiants / groupe.capacite_max * 100) if groupe.capacite_max > 0 else 0
        nouveau_places_disponibles = groupe.capacite_max - nouveau_nombre_etudiants
        
        return jsonify({
            'success': True, 
            'message': f'Étudiant {etudiant.nom_complet} inscrit avec succès dans le groupe générique {groupe.code}',
            'nouveau_nombre_etudiants': nouveau_nombre_etudiants,
            'nouveau_taux_remplissage': round(nouveau_taux_remplissage, 1),
            'nouveau_places_disponibles': nouveau_places_disponibles,
            'etudiant': {
                'id': etudiant.id,
                'matricule': etudiant.matricule,
                'nom': etudiant.nom,
                'prenom': etudiant.prenom
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de l\'inscription: {str(e)}'})

@bp.route('/groupes-generiques/<int:groupe_id>/desinscrire-etudiant', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def desinscrire_etudiant_groupe_generique(groupe_id):
    """Désinscrire un étudiant d'un groupe générique"""
    from flask import jsonify, request
    from app.models.academique import GroupeGenerique, InscriptionGroupeGenerique
    
    try:
        data = request.get_json()
        etudiant_id = data.get('etudiant_id')
        
        if not etudiant_id:
            return jsonify({'success': False, 'message': 'ID étudiant manquant'})
        
        groupe = GroupeGenerique.query.get_or_404(groupe_id)
        etudiant = Etudiant.query.get_or_404(etudiant_id)
        
        # Vérifier si l'étudiant est inscrit
        inscription_existante = InscriptionGroupeGenerique.query.filter_by(
            etudiant_id=etudiant_id, 
            groupe_generique_id=groupe_id
        ).first()
        
        if not inscription_existante:
            return jsonify({'success': False, 'message': f'L\'étudiant {etudiant.nom_complet} n\'est pas inscrit dans ce groupe générique'})
        
        # Supprimer l'inscription
        db.session.delete(inscription_existante)
        db.session.commit()
        
        # Calculer les nouvelles statistiques
        nouveau_nombre_etudiants = len(groupe.etudiants)
        nouveau_taux_remplissage = (nouveau_nombre_etudiants / groupe.capacite_max * 100) if groupe.capacite_max > 0 else 0
        nouveau_places_disponibles = groupe.capacite_max - nouveau_nombre_etudiants
        
        return jsonify({
            'success': True, 
            'message': f'Étudiant {etudiant.nom_complet} désinscrit avec succès du groupe générique {groupe.code}',
            'nouveau_nombre_etudiants': nouveau_nombre_etudiants,
            'nouveau_taux_remplissage': round(nouveau_taux_remplissage, 1),
            'nouveau_places_disponibles': nouveau_places_disponibles,
            'etudiant': {
                'id': etudiant.id,
                'matricule': etudiant.matricule,
                'nom': etudiant.nom,
                'prenom': etudiant.prenom
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la désinscription: {str(e)}'})

@bp.route('/groupes-generiques/<int:groupe_id>/lier-toutes-ues', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def lier_groupe_generique_toutes_ues(groupe_id):
    """Lier un groupe générique à toutes les UE"""
    ues = ServiceAcademique.obtenir_toutes_unites_enseignement()
    succes_count = 0
    
    for ue in ues:
        if ServiceAcademique.lier_groupe_generique_ue(groupe_id, ue.id):
            succes_count += 1
    
    if succes_count > 0:
        flash(f'Groupe générique lié à {succes_count} UE(s) avec succès!', 'success')
    else:
        flash('Aucune nouvelle liaison créée.', 'info')
    
    return redirect(url_for('admin.details_groupe_generique', groupe_id=groupe_id))

@bp.route('/ues/<int:ue_id>/lier-tous-groupes', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def lier_tous_groupes_generiques_ue(ue_id):
    """Lier tous les groupes génériques à une UE"""
    success = ServiceAcademique.lier_groupes_generiques_a_ue(ue_id)
    
    if success:
        flash('Tous les groupes génériques ont été liés à cette UE!', 'success')
    else:
        flash('Erreur lors de la liaison des groupes génériques.', 'error')
    
    return redirect(url_for('admin.details_unite_enseignement', ue_id=ue_id))

@bp.route('/pedagogique/note/<int:note_id>')
@login_required
@utilisateur_actif_requis
@administrateur_requis
def detail_note(note_id):
    """Voir les détails d'une note"""
    from app.models.pedagogique import Note
    
    note = Note.query.get_or_404(note_id)
    
    return render_template('admin/pedagogique/detail_note.html', note=note)

@bp.route('/pedagogique/valider-notes-masse', methods=['POST'])
@login_required
@utilisateur_actif_requis
@administrateur_requis
def valider_notes_masse():
    """Valider plusieurs notes en masse"""
    from app.models.pedagogique import Note
    
    note_ids = request.form.getlist('note_ids')
    commentaire = request.form.get('commentaire', 'Validation en masse par l\'administrateur')
    
    if not note_ids:
        flash('Aucune note sélectionnée', 'error')
        return redirect(url_for('admin.validation_notes'))
    
    try:
        notes = Note.query.filter(Note.id.in_(note_ids)).all()
        
        for note in notes:
            note.validee = True
            note.validee_par = current_user.id
            note.date_validation = datetime.utcnow()
            note.commentaire_validation = commentaire
        
        db.session.commit()
        flash(f'{len(notes)} note(s) validée(s) avec succès', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la validation: {str(e)}', 'error')
    
    return redirect(url_for('admin.validation_notes'))
