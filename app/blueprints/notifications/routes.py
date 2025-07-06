"""
Routes de notifications pour Edusco
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.notifications import bp
from app.models.utilisateur import Notification
from app.extensions import db
from app.services.notification import ServiceNotification

@bp.route('/')
def index():
    """Page d'accueil des notifications"""
    return redirect(url_for('notifications.liste'))

@bp.route('/liste')
@login_required
def liste():
    """Liste des notifications de l'utilisateur connecté"""
    service_notification = ServiceNotification()
    notifications = service_notification.get_notifications_utilisateur(current_user.id)
    return render_template('notifications/liste.html', notifications=notifications)

@bp.route('/<int:notification_id>/marquer-lue')
@login_required
def marquer_lue(notification_id):
    """Marquer une notification comme lue"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Vérifier que la notification appartient à l'utilisateur connecté
    if notification.utilisateur_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('notifications.liste'))
    
    notification.lue = True
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Notification marquée comme lue', 'success')
    return redirect(url_for('notifications.liste'))

@bp.route('/<int:notification_id>/supprimer')
@login_required
def supprimer(notification_id):
    """Supprimer une notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Vérifier que la notification appartient à l'utilisateur connecté
    if notification.utilisateur_id != current_user.id:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('notifications.liste'))
    
    db.session.delete(notification)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Notification supprimée', 'success')
    return redirect(url_for('notifications.liste'))

@bp.route('/marquer-toutes-lues')
@login_required
def marquer_toutes_lues():
    """Marquer toutes les notifications comme lues"""
    notifications = Notification.query.filter_by(
        utilisateur_id=current_user.id,
        lue=False
    ).all()
    
    for notification in notifications:
        notification.lue = True
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Toutes les notifications ont été marquées comme lues', 'success')
    return redirect(url_for('notifications.liste'))

@bp.route('/supprimer-toutes')
@login_required
def supprimer_toutes():
    """Supprimer toutes les notifications de l'utilisateur"""
    notifications = Notification.query.filter_by(
        utilisateur_id=current_user.id
    ).all()
    
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    flash('Toutes les notifications ont été supprimées', 'success')
    return redirect(url_for('notifications.liste')) 