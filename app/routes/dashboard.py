from flask import Blueprint, render_template
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

    # Recent activities from followed users
    feed_activities = current_user.get_feed_activities(limit=5)

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
        'knowledge_score': current_user.knowledge_score,
        'categories_count': len(categories),
        'library_count': Library.query.filter_by(user_id=current_user.id).count()
    }

    return render_template('dashboard.html',
                           certificates=certificates,
                           recent_library=recent_library,
                           upcoming_events=upcoming_events,
                           feed_activities=feed_activities,
                           knowledge_identity=knowledge_identity,
                           stats=stats)
