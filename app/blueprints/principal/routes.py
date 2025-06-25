"""
Routes principales pour Edusco
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.principal import bp
from app.services.notification import ServiceNotification

@bp.route('/')
def accueil():
    """Page d'accueil publique"""
    return render_template('principal/accueil.html')

@bp.route('/apropos')
def apropos():
    """Page à propos"""
    return render_template('principal/apropos.html')

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