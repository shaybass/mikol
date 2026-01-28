from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import Activity, Event

feed_bp = Blueprint('feed', __name__, url_prefix='/feed')


@feed_bp.route('/')
@login_required
def home():
    """Show feed of activities from followed users"""
    # Get activities from users the current user follows
    feed_activities = current_user.get_feed_activities(limit=50)

    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.status == 'published'
    ).order_by(Event.date.desc()).limit(5).all()

    # Get suggested users to follow (users with most certificates who current user doesn't follow)
    from app.models import User
    from sqlalchemy import func

    following_ids = [u.id for u in current_user.get_following(100)]
    following_ids.append(current_user.id)

    suggested_users = User.query.filter(
        ~User.id.in_(following_ids)
    ).order_by(func.random()).limit(5).all()

    return render_template('feed/home.html',
                           activities=feed_activities,
                           upcoming_events=upcoming_events,
                           suggested_users=suggested_users)
