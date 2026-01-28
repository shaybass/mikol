"""
Certificate Service - Core business logic for MIKOL's knowledge certificates.

Handles:
- Certificate issuance (individual + batch)
- Auto-save to user's library
- Share URL generation
- Share metadata for social platforms
"""
from datetime import datetime
from urllib.parse import quote

from flask import current_app
from app import db
from app.models import Certificate, Library, EventParticipation, Activity


def issue_certificate(event, user_id, role):
    """
    Issue a knowledge certificate for a user's participation in an event.
    Also auto-saves it to the user's library.

    Returns the certificate (existing or newly created).
    """
    # Use Event's built-in issuance which snapshots all data
    cert = event.issue_certificate(user_id, role)
    db.session.flush()

    # Auto-save to user's library
    existing_library = Library.query.filter_by(
        user_id=user_id,
        certificate_id=cert.id
    ).first()

    if not existing_library:
        library_item = Library(
            user_id=user_id,
            certificate_id=cert.id,
            saved_at=datetime.utcnow()
        )
        db.session.add(library_item)

    # Link participation to certificate
    participation = EventParticipation.query.filter_by(
        event_id=event.id,
        user_id=user_id
    ).first()
    if participation and not participation.certificate_id:
        participation.certificate_id = cert.id

    # Log activity
    Activity.log_activity(
        user_id=user_id,
        activity_type='received_certificate',
        content={
            'event_id': event.id,
            'event_title': event.title,
            'role': role,
            'certificate_id': cert.id
        }
    )

    return cert


def issue_certificates_for_event(event):
    """
    Issue certificates for all participants of a completed event.
    Returns the number of new certificates created.
    """
    participations = EventParticipation.query.filter_by(event_id=event.id).all()
    certificates_created = 0

    for participation in participations:
        existing = Certificate.query.filter_by(
            event_id=event.id,
            user_id=participation.user_id
        ).first()

        if not existing:
            cert = issue_certificate(event, participation.user_id, participation.role)
            certificates_created += 1

    return certificates_created


def generate_share_url(certificate):
    """Generate a public shareable URL for a certificate."""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    return f"{base_url}/certificates/public/{certificate.share_token}"


def get_share_text(certificate):
    """
    Generate the fixed share text per spec: "השתתפתי באירוע [Event Name]"
    """
    event_title = certificate.title or certificate.event.title
    return f"השתתפתי באירוע {event_title}"


def get_share_metadata(certificate, platform):
    """
    Return platform-specific share data for a certificate.
    Uses fixed Hebrew share text per spec.
    """
    url = generate_share_url(certificate)
    share_text = get_share_text(certificate)

    encoded_url = quote(url, safe='')
    encoded_text = quote(share_text, safe='')

    if platform == 'linkedin':
        return {
            'url': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
            'text': share_text
        }
    elif platform == 'facebook':
        return {
            'url': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_text}",
            'text': share_text
        }
    elif platform == 'twitter':
        return {
            'url': f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
            'text': share_text
        }
    elif platform == 'whatsapp':
        wa_text = quote(f"{share_text}\n{url}", safe='')
        return {
            'url': f"https://wa.me/?text={wa_text}",
            'text': share_text
        }
    elif platform == 'copy':
        return {
            'url': url,
            'text': share_text
        }

    return {'url': url, 'text': share_text}
