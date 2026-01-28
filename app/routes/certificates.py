from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Certificate, Library, Activity
from app.services.certificate_service import get_share_metadata, get_share_text

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')


@certificates_bp.route('/my')
@login_required
def my_certificates():
    certificates = Certificate.query.filter_by(user_id=current_user.id)\
        .order_by(Certificate.issued_at.desc()).all()
    return render_template('certificates/my.html', certificates=certificates)


@certificates_bp.route('/<share_token>')
def view_certificate(share_token):
    certificate = Certificate.query.filter_by(share_token=share_token).first_or_404()

    # Check if current user has saved this certificate
    is_saved = False
    is_owner = False
    if current_user.is_authenticated:
        is_owner = current_user.id == certificate.user_id
        is_saved = Library.query.filter_by(
            user_id=current_user.id,
            certificate_id=certificate.id
        ).first() is not None

    # Build share links
    share_links = {
        'linkedin': get_share_metadata(certificate, 'linkedin')['url'],
        'facebook': get_share_metadata(certificate, 'facebook')['url'],
        'twitter': get_share_metadata(certificate, 'twitter')['url'],
        'whatsapp': get_share_metadata(certificate, 'whatsapp')['url'],
    }

    return render_template('certificates/view.html',
                           certificate=certificate,
                           is_saved=is_saved,
                           is_owner=is_owner,
                           share_links=share_links)


@certificates_bp.route('/public/<token>')
def view_public_certificate(token):
    """
    Public certificate view - shareable, no login required.
    This is the page people see when they scan QR or click share link.
    Two-button flow: "Collect" or "Collect + Share"
    """
    certificate = Certificate.query.filter_by(share_token=token).first_or_404()

    if not certificate.is_public:
        flash('This certificate is private.', 'info')
        return redirect(url_for('events.list_events'))

    # Check if user already collected this certificate
    is_collected = False
    is_owner = False
    if current_user.is_authenticated:
        is_owner = current_user.id == certificate.user_id
        is_collected = Library.query.filter_by(
            user_id=current_user.id,
            certificate_id=certificate.id
        ).first() is not None

    # Build share links for each platform
    share_links = {
        'linkedin': get_share_metadata(certificate, 'linkedin')['url'],
        'facebook': get_share_metadata(certificate, 'facebook')['url'],
        'twitter': get_share_metadata(certificate, 'twitter')['url'],
        'whatsapp': get_share_metadata(certificate, 'whatsapp')['url'],
    }

    return render_template('certificates/public.html',
                           certificate=certificate,
                           share_links=share_links,
                           is_collected=is_collected,
                           is_owner=is_owner)


@certificates_bp.route('/<token>/collect', methods=['POST'])
@login_required
def collect_certificate(token):
    """
    Collect certificate - add to user's library.
    Single-click action.
    """
    certificate = Certificate.query.filter_by(share_token=token).first_or_404()

    # Check if already collected
    existing = Library.query.filter_by(
        user_id=current_user.id,
        certificate_id=certificate.id
    ).first()

    if existing:
        flash('Certificate already in your library!', 'info')
        return redirect(url_for('certificates.view_certificate', share_token=token))

    # Add to library
    library_item = Library(
        user_id=current_user.id,
        certificate_id=certificate.id
    )
    db.session.add(library_item)

    # Log activity
    Activity.log_activity(
        user_id=current_user.id,
        activity_type='collected_certificate',
        content={
            'certificate_id': certificate.id,
            'event_title': certificate.event.title
        }
    )

    db.session.commit()

    flash('Certificate collected!', 'success')
    return redirect(url_for('certificates.view_certificate', share_token=token))


@certificates_bp.route('/<token>/collect-and-share', methods=['POST'])
@login_required
def collect_and_share(token):
    """
    Collect certificate and prepare for sharing.
    Collects first, then shows share options.
    """
    certificate = Certificate.query.filter_by(share_token=token).first_or_404()

    # Check if already collected
    existing = Library.query.filter_by(
        user_id=current_user.id,
        certificate_id=certificate.id
    ).first()

    if not existing:
        # Add to library
        library_item = Library(
            user_id=current_user.id,
            certificate_id=certificate.id
        )
        db.session.add(library_item)

        # Log activity
        Activity.log_activity(
            user_id=current_user.id,
            activity_type='collected_certificate',
            content={
                'certificate_id': certificate.id,
                'event_title': certificate.event.title
            }
        )
        db.session.commit()

    # Redirect to share page
    return redirect(url_for('certificates.share_certificate', token=token))


@certificates_bp.route('/<token>/share')
@login_required
def share_certificate(token):
    """
    Share page - shows all share options after collection.
    """
    certificate = Certificate.query.filter_by(share_token=token).first_or_404()

    # Fixed Hebrew share text per spec
    share_text = get_share_text(certificate)

    share_links = {
        'linkedin': get_share_metadata(certificate, 'linkedin')['url'],
        'facebook': get_share_metadata(certificate, 'facebook')['url'],
        'twitter': get_share_metadata(certificate, 'twitter')['url'],
        'whatsapp': get_share_metadata(certificate, 'whatsapp')['url'],
    }

    return render_template('certificates/share.html',
                           certificate=certificate,
                           share_links=share_links,
                           share_text=share_text)


@certificates_bp.route('/<int:cert_id>/save', methods=['POST'])
@login_required
def save_certificate(cert_id):
    certificate = Certificate.query.get_or_404(cert_id)

    existing = Library.query.filter_by(
        user_id=current_user.id,
        certificate_id=cert_id
    ).first()

    if existing:
        flash('Certificate already in your library.', 'info')
        return redirect(url_for('certificates.view_certificate',
                                share_token=certificate.share_token))

    library_item = Library(
        user_id=current_user.id,
        certificate_id=cert_id
    )
    db.session.add(library_item)
    db.session.commit()

    flash('Certificate saved to your library!', 'success')
    return redirect(url_for('certificates.view_certificate',
                            share_token=certificate.share_token))
