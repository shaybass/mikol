from datetime import datetime
import json

from app import db


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    # Types: created_event, received_certificate, shared_certificate, followed_user, joined_mikol
    content = db.Column(db.Text)  # JSON content
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='activities')

    def set_content(self, data):
        """Set content as JSON."""
        self.content = json.dumps(data)

    def get_content(self):
        """Get content as dict."""
        if self.content:
            return json.loads(self.content)
        return {}

    @staticmethod
    def log_activity(user_id, activity_type, content=None):
        """Helper to log a new activity."""
        activity = Activity(
            user_id=user_id,
            activity_type=activity_type
        )
        if content:
            activity.set_content(content)
        db.session.add(activity)
        return activity

    def __repr__(self):
        return f'<Activity {self.user_id} {self.activity_type}>'
