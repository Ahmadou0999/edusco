"""
Routes principales pour Edusco
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from app.models.academique import AnneeAcademique, Semestre, UniteEnseignement, Matiere, Etudiant, Enseignant, Groupe
from app.services.academique import ServiceAcademique
from app.services.pedagogique import ServicePedagogique
from app import db
from app.services.notification import ServiceNotification
from app.blueprints.principal import bp
from app.services.authentification import ServiceAuthentification
from app.forms.authentification import ConnexionForm, InscriptionForm, ChangementMotDePasseForm
from datetime import datetime

# ==================== ROUTES D'AUTHENTIFICATION ====================

@bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('principal.dashboard'))
    
    form = ConnexionForm()
    if form.validate_on_submit():
        service_auth = ServiceAuthentification()
        utilisateur, succes = service_auth.authentifier_utilisateur(
            form.email.data, form.mot_de_passe.data
        )
        
        if succes and utilisateur:
            login_user(utilisateur, remember=form.se_souvenir.data)
            flash(f'Bienvenue {utilisateur.prenom} {utilisateur.nom} !', 'success')
            
            # Redirection selon le rôle
            if utilisateur.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif utilisateur.role == 'enseignant':
                return redirect(url_for('enseignant.dashboard'))
            elif utilisateur.role == 'etudiant':
                return redirect(url_for('etudiant.dashboard'))
            else:
                return redirect(url_for('principal.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('authentification/connexion.html', form=form)

@bp.route('/deconnexion')
def deconnexion():
    """Déconnexion de l'utilisateur"""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('principal.accueil'))

@bp.route('/mot-de-passe-oublie', methods=['GET', 'POST'])
def mot_de_passe_oublie():
    """Page de mot de passe oublié"""
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            service_auth = ServiceAuthentification()
            succes = service_auth.demander_reinitialisation_mot_de_passe(email)
            if succes:
                flash('Un email de réinitialisation a été envoyé.', 'success')
            else:
                flash('Email non trouvé dans notre base de données.', 'error')
        else:
            flash('Veuillez saisir votre adresse email.', 'error')
    
    return render_template('authentification/mot_de_passe_oublie.html')

@bp.route('/reinitialiser-mot-de-passe/<token>', methods=['GET', 'POST'])
def reinitialiser_mot_de_passe(token):
    """Réinitialisation du mot de passe avec token"""
    service_auth = ServiceAuthentification()
    utilisateur = service_auth.verifier_token_reinitialisation(token)
    
    if not utilisateur:
        flash('Token invalide ou expiré.', 'error')
        return redirect(url_for('principal.connexion'))
    
    form = ChangementMotDePasseForm()
    if form.validate_on_submit():
        succes = service_auth.reinitialiser_mot_de_passe(token, form.nouveau_mot_de_passe.data)
        if succes:
            flash('Votre mot de passe a été réinitialisé avec succès.', 'success')
            return redirect(url_for('principal.connexion'))
        else:
            flash('Erreur lors de la réinitialisation du mot de passe.', 'error')
    
    return render_template('authentification/reinitialiser_mot_de_passe.html', form=form)

# ==================== ROUTES PUBLIQUES ====================

@bp.route('/')
def accueil():
    """Page d'accueil publique"""
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    # Statistiques publiques
    stats = {
        'total_etudiants': service_academique.compter_etudiants(),
        'total_enseignants': service_academique.compter_enseignants(),
        'total_matieres': service_academique.compter_matieres(),
        'annee_actuelle': service_academique.get_annee_academique_actuelle()
    }
    
    # Informations sur l'année académique actuelle
    annee_actuelle = service_academique.get_annee_academique_actuelle()
    
    # Dernières actualités (à implémenter selon les besoins)
    actualites = []
    
    return render_template('principal/accueil.html', 
                         stats=stats,
                         annee_actuelle=annee_actuelle,
                         actualites=actualites)

@bp.route('/apropos')
def apropos():
    """Page à propos de l'institut"""
    return render_template('principal/apropos.html')

@bp.route('/contact')
def contact():
    """Page de contact"""
    # On vérifie si un formulaire est attendu, sinon on passe un dummy form
    class DummyForm:
        nom = email = sujet = message = type('Field', (), {'errors': []})()
        def hidden_tag(self):
            return ''
    form = DummyForm()
    return render_template('principal/contact.html', form=form)

@bp.route('/actualites')
def actualites():
    """Page des actualités"""
    # À implémenter selon les besoins
    actualites = []
    return render_template('principal/actualites.html', actualites=actualites)

@bp.route('/admission')
def admission():
    """Page d'information sur l'admission"""
    return render_template('principal/admission.html')

@bp.route('/programmes')
def programmes():
    """Page des programmes d'études"""
    service_academique = ServiceAcademique()
    unites_enseignement = service_academique.get_unites_enseignement_actives()
    
    return render_template('principal/programmes.html', 
                         unites_enseignement=unites_enseignement)

@bp.route('/equipe')
def equipe():
    """Page de l'équipe enseignante"""
    service_academique = ServiceAcademique()
    enseignants = service_academique.get_enseignants_actifs()
    
    return render_template('principal/equipe.html', 
                         enseignants=enseignants)

@bp.route('/resultats')
def resultats():
    """Page des résultats académiques (publique)"""
    service_pedagogique = ServicePedagogique()
    
    # Filtres
    annee_id = request.args.get('annee_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    unite_id = request.args.get('unite_id', type=int)
    
    # Récupérer les résultats selon les filtres
    resultats = service_pedagogique.get_resultats_publics(
        annee_id=annee_id,
        semestre_id=semestre_id,
        unite_id=unite_id
    )
    
    # Options pour les filtres
    service_academique = ServiceAcademique()
    annees = service_academique.get_annees_academiques()
    semestres = service_pedagogique.get_semestres_actifs()
    unites = service_academique.get_unites_enseignement_actives()
    
    return render_template('principal/resultats.html',
                         resultats=resultats,
                         annees=annees,
                         semestres=semestres,
                         unites=unites)

@bp.route('/recherche')
def recherche():
    """Page de recherche d'étudiants (publique)"""
    query = request.args.get('q', '')
    type_recherche = request.args.get('type', 'etudiant')
    
    if not query:
        return render_template('principal/recherche.html', 
                             resultats=None, 
                             query=query, 
                             type_recherche=type_recherche)
    
    service_academique = ServiceAcademique()
    
    if type_recherche == 'etudiant':
        resultats = service_academique.rechercher_etudiants(query)
    elif type_recherche == 'enseignant':
        resultats = service_academique.rechercher_enseignants(query)
    else:
        resultats = []
    
    return render_template('principal/recherche.html',
                         resultats=resultats,
                         query=query,
                         type_recherche=type_recherche)

@bp.route('/etudiant/<int:etudiant_id>')
def profil_etudiant(etudiant_id):
    """Profil public d'un étudiant"""
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    etudiant = service_academique.get_etudiant_par_id(etudiant_id)
    
    if not etudiant:
        flash('Étudiant non trouvé', 'error')
        return redirect(url_for('principal.recherche'))
    
    # Informations académiques
    informations_academiques = service_academique.get_informations_academiques_etudiant(etudiant_id)
    
    # Résultats académiques (limités aux informations publiques)
    resultats = service_pedagogique.get_resultats_etudiant_publics(etudiant_id)
    
    return render_template('principal/profil_etudiant.html',
                         etudiant=etudiant,
                         informations_academiques=informations_academiques,
                         resultats=resultats)

@bp.route('/enseignant/<int:enseignant_id>')
def profil_enseignant(enseignant_id):
    """Profil public d'un enseignant"""
    service_academique = ServiceAcademique()
    
    enseignant = service_academique.get_enseignant_par_id(enseignant_id)
    
    if not enseignant:
        flash('Enseignant non trouvé', 'error')
        return redirect(url_for('principal.recherche'))
    
    # Matières enseignées
    matieres = enseignant.matieres
    
    # Groupes enseignés
    groupes = enseignant.groupes
    
    return render_template('principal/profil_enseignant.html',
                         enseignant=enseignant,
                         matieres=matieres,
                         groupes=groupes)

@bp.route('/calendrier-academique')
def calendrier_academique():
    """Calendrier académique public"""
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    
    # Année académique actuelle
    annee_actuelle = service_academique.get_annee_academique_actuelle()
    
    # Semestres de l'année actuelle
    semestres = []
    if annee_actuelle:
        semestres = service_pedagogique.get_semestres_par_annee(annee_actuelle.id)
    
    # Événements académiques (à implémenter selon les besoins)
    evenements = []
    
    return render_template('principal/calendrier_academique.html',
                         annee_actuelle=annee_actuelle,
                         semestres=semestres,
                         evenements=evenements)

@bp.route('/mentions-legales')
def mentions_legales():
    """Page des mentions légales"""
    return render_template('principal/mentions_legales.html')

@bp.route('/politique-confidentialite')
def politique_confidentialite():
    """Page de la politique de confidentialité"""
    return render_template('principal/politique_confidentialite.html')

@bp.route('/conditions-utilisation')
def conditions_utilisation():
    """Page des conditions d'utilisation"""
    return render_template('principal/conditions_utilisation.html')

# Routes pour les utilisateurs connectés
@bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord pour les utilisateurs connectés"""
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'enseignant':
        return redirect(url_for('enseignant.dashboard'))
    elif current_user.role == 'etudiant':
        return redirect(url_for('etudiant.dashboard'))
    else:
        flash('Rôle utilisateur non reconnu', 'error')
        return redirect(url_for('principal.accueil'))

@bp.route('/profil')
@login_required
def profil():
    """Profil de l'utilisateur connecté"""
    if current_user.role == 'admin':
        return redirect(url_for('admin.profil'))
    elif current_user.role == 'enseignant':
        return redirect(url_for('enseignant.profil'))
    elif current_user.role == 'etudiant':
        return redirect(url_for('etudiant.profil'))
    else:
        flash('Rôle utilisateur non reconnu', 'error')
        return redirect(url_for('principal.accueil'))

@bp.route('/changer-mot-de-passe', methods=['GET', 'POST'])
@login_required
def changer_mot_de_passe():
    """Redirection vers la route d'authentification pour changer le mot de passe"""
    return redirect(url_for('authentification.changer_mot_de_passe'))

# Routes pour les notifications
@bp.route('/notifications')
@login_required
def notifications():
    """Afficher les notifications de l'utilisateur"""
    notifications = ServiceNotification.get_user_notifications(current_user.id)
    return render_template('notifications/liste.html', notifications=notifications)

@bp.route('/notifications/<int:notification_id>/marquer-lue')
@login_required
def marquer_notification_lue(notification_id):
    """Marquer une notification comme lue"""
    success = ServiceNotification.marquer_lue(notification_id, current_user.id)
    if success:
        flash('Notification marquée comme lue', 'success')
    else:
        flash('Erreur lors du marquage de la notification', 'error')
    return redirect(url_for('principal.notifications'))

@bp.route('/notifications/<int:notification_id>/supprimer')
@login_required
def supprimer_notification(notification_id):
    """Supprimer une notification"""
    success = ServiceNotification.supprimer_notification(notification_id, current_user.id)
    if success:
        flash('Notification supprimée avec succès', 'success')
    else:
        flash('Erreur lors de la suppression de la notification', 'error')
    return redirect(url_for('principal.notifications'))

@bp.route('/emplois-du-temps')
def emplois_du_temps():
    """Page publique des emplois du temps"""
    service_academique = ServiceAcademique()
    service_pedagogique = ServicePedagogique()
    groupes = service_academique.get_groupes_actifs() if hasattr(service_academique, 'get_groupes_actifs') else []
    enseignants = service_academique.get_enseignants_actifs() if hasattr(service_academique, 'get_enseignants_actifs') else []
    emplois_du_temps = []  # À remplacer par la vraie récupération
    horaires = ["08:00-10:00", "10:00-12:00", "13:00-15:00", "15:00-17:00"]
    return render_template('principal/emplois_du_temps.html', groupes=groupes, enseignants=enseignants, emplois_du_temps=emplois_du_temps, horaires=horaires)

@bp.route('/evenements')
def evenements():
    """Page publique des événements"""
    evenements = []  # À remplacer par la vraie récupération
    return render_template('principal/evenements.html', evenements=evenements)

@bp.route('/messagerie')
@login_required
def messagerie():
    """Page principale de la messagerie"""
    from app.models.utilisateur import Message
    from app.models.utilisateur import Utilisateur
    
    # Récupérer les messages reçus et envoyés
    messages_recus = Message.query.filter_by(destinataire_id=current_user.id)\
        .order_by(Message.date_envoi.desc()).limit(10).all()
    
    messages_envoyes = Message.query.filter_by(expediteur_id=current_user.id)\
        .order_by(Message.date_envoi.desc()).limit(10).all()
    
    # Compter les messages non lus
    messages_non_lus = Message.query.filter_by(destinataire_id=current_user.id, lu=False).count()
    
    return render_template('principal/messagerie.html',
                         messages_recus=messages_recus,
                         messages_envoyes=messages_envoyes,
                         messages_non_lus=messages_non_lus)

@bp.route('/messagerie/envoyer', methods=['GET', 'POST'])
@login_required
def envoyer_message():
    """Envoyer un nouveau message"""
    from app.models.utilisateur import Message, Utilisateur
    from app.extensions import db
    
    if request.method == 'POST':
        destinataire_id = request.form.get('destinataire_id', type=int)
        sujet = request.form.get('sujet', '').strip()
        contenu = request.form.get('contenu', '').strip()
        
        if not destinataire_id or not sujet or not contenu:
            flash('Tous les champs sont obligatoires', 'error')
            return redirect(url_for('principal.envoyer_message'))
        
        # Vérifier que le destinataire existe
        destinataire = Utilisateur.query.get(destinataire_id)
        if not destinataire:
            flash('Destinataire non trouvé', 'error')
            return redirect(url_for('principal.envoyer_message'))
        
        # Créer le message
        message = Message(
            expediteur_id=current_user.id,
            destinataire_id=destinataire_id,
            sujet=sujet,
            contenu=contenu
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash('Message envoyé avec succès', 'success')
        return redirect(url_for('principal.messagerie'))
    
    # GET - Afficher le formulaire
    utilisateurs = Utilisateur.query.filter(Utilisateur.id != current_user.id).all()
    
    return render_template('principal/envoyer_message.html', utilisateurs=utilisateurs)

@bp.route('/messagerie/message/<int:message_id>')
@login_required
def voir_message(message_id):
    """Voir un message spécifique"""
    from app.models.utilisateur import Message
    from app.extensions import db
    
    message = Message.query.get_or_404(message_id)
    
    # Vérifier que l'utilisateur peut voir ce message
    if message.expediteur_id != current_user.id and message.destinataire_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.messagerie'))
    
    # Marquer comme lu si c'est le destinataire
    if message.destinataire_id == current_user.id and not message.lu:
        message.lu = True
        message.date_lecture = datetime.utcnow()
        db.session.commit()
    
    return render_template('principal/voir_message.html', message=message)

@bp.route('/messagerie/supprimer/<int:message_id>', methods=['POST'])
@login_required
def supprimer_message(message_id):
    """Supprimer un message"""
    from app.models.utilisateur import Message
    from app.extensions import db
    
    message = Message.query.get_or_404(message_id)
    
    # Vérifier que l'utilisateur peut supprimer ce message
    if message.expediteur_id != current_user.id and message.destinataire_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('principal.messagerie'))
    
    db.session.delete(message)
    db.session.commit()
    
    flash('Message supprimé avec succès', 'success')
    return redirect(url_for('principal.messagerie')) 