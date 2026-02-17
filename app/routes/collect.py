"""
Collection routes — public fast-collection flow for events.
"""
from datetime import datetime
import secrets

from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import current_user
from flask_wtf.csrf import generate_csrf

from app import db, csrf
from app.models import Event, User, EventParticipation, Certificate
from app.services.certificate_service import issue_certificate

collect_bp = Blueprint('collect', __name__)


@collect_bp.route('/collect/<event_code>')
def collect_page(event_code):
    """Public event collection page — no auth required."""
    event = Event.query.filter_by(collection_code=event_code).first_or_404()
    return render_template('collect/collect.html', event=event)


@collect_bp.route('/collect/<event_code>/submit', methods=['POST'])
@csrf.exempt
def collect_submit(event_code):
    """Handle collection submission — AJAX endpoint."""
    event = Event.query.filter_by(collection_code=event_code).first_or_404()

    if not event.is_collection_active:
        return jsonify({'success': False, 'error': 'האיסוף סגור כרגע'}), 400

    # Determine user
    if current_user.is_authenticated:
        user = current_user
    else:
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()

        if not name or not email:
            return jsonify({'success': False, 'error': 'נא למלא שם ואימייל'}), 400

        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
            )
            user.set_password(secrets.token_urlsafe(16))
            db.session.add(user)
            db.session.flush()

    # Check if already collected
    existing_cert = Certificate.query.filter_by(event_id=event.id, user_id=user.id).first()
    if existing_cert:
        return jsonify({
            'success': True,
            'already': True,
            'message': 'כבר אספת אישור לאירוע זה!',
            'cert_url': f'/certificates/public/{existing_cert.share_token}'
        })

    # Ensure participation exists
    participation = EventParticipation.query.filter_by(event_id=event.id, user_id=user.id).first()
    if not participation:
        participation = EventParticipation(
            event_id=event.id,
            user_id=user.id,
            role='participant'
        )
        db.session.add(participation)
        db.session.flush()

    # Issue certificate
    cert = issue_certificate(event, user.id, 'participant')
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '✅ אישור נאסף בהצלחה!',
        'cert_url': f'/certificates/public/{cert.share_token}'
    })
