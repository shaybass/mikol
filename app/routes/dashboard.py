from datetime import datetime
from io import StringIO
import csv

from flask import Blueprint, render_template, abort, make_response
from flask_login import login_required, current_user

from app.models import Certificate, Library, Event, Activity

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Knowledge-first home page for authenticated users."""
    # Knowledge stats
    certificates = Certificate.query.filter_by(user_id=current_user.id)\
        .order_by(Certificate.issued_at.desc()).all()

    # Recent library items (last 3)
    recent_library = Library.query.filter_by(user_id=current_user.id)\
        .order_by(Library.saved_at.desc()).limit(3).all()

    # Upcoming events (knowledge opportunities)
    upcoming_events = Event.query.filter(
        Event.status == 'published'
    ).order_by(Event.date.asc()).limit(5).all()

    # Knowledge identity
    knowledge_identity = current_user.get_knowledge_identity()

    # Categories from certificates
    categories = set()
    for cert in certificates:
        meta = cert.cert_metadata
        if meta and meta.get('category'):
            categories.add(meta['category'])

    stats = {
        'total_certificates': len(certificates),
        'knowledge_score': 0,  # removed for MVP
        'categories_count': len(categories),
        'library_count': Library.query.filter_by(user_id=current_user.id).count()
    }

    # Phase 4: Organizer section
    organized_events = Event.query.filter_by(organizer_id=current_user.id)\
        .order_by(Event.date.desc()).all()

    # Monthly usage: certificates issued this month across organizer's events
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_issued = 0
    if organized_events:
        org_event_ids = [e.id for e in organized_events]
        monthly_issued = Certificate.query.filter(
            Certificate.event_id.in_(org_event_ids),
            Certificate.issued_at >= month_start
        ).count()

    return render_template('dashboard.html',
                           certificates=certificates,
                           recent_library=recent_library,
                           upcoming_events=upcoming_events,
                           knowledge_identity=knowledge_identity,
                           stats=stats,
                           organized_events=organized_events,
                           monthly_issued=monthly_issued)


@dashboard_bp.route('/events/<int:event_id>/export-csv')
@login_required
def export_csv(event_id):
    """Export participants list as CSV. Only accessible by event organizer."""
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        abort(403)

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Name', 'Email', 'Role', 'Issued At'])

    certs = Certificate.query.filter_by(event_id=event_id).all()
    for cert in certs:
        writer.writerow([
            cert.user.name,
            cert.user.email,
            cert.role,
            cert.issued_at.strftime('%Y-%m-%d %H:%M') if cert.issued_at else ''
        ])

    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = f'attachment; filename=event_{event_id}_participants.csv'
    output.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return output
