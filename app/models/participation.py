from datetime import datetime
import json

from app import db


class EventParticipation(db.Model):
    __tablename__ = 'event_participations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # organizer, speaker, participant, host
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-tagging: participant's social links to appear on certificate
    social_links_json = db.Column(db.Text)  # JSON: {"linkedin": "url", "twitter": "url", "instagram": "url"}
    display_on_certificate = db.Column(db.Boolean, default=True)  # Whether to show on public certificate

    # Link to issued certificate
    certificate = db.relationship('Certificate', backref='participation', foreign_keys=[certificate_id])

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='unique_event_user'),
    )

    @property
    def social_links(self):
        """Social links for this participation."""
        if self.social_links_json:
            return json.loads(self.social_links_json)
        return {}

    @social_links.setter
    def social_links(self, value):
        self.social_links_json = json.dumps(value) if value else None

    def get_participant_display(self):
        """Get participant info for certificate display."""
        return {
            'user_id': self.user_id,
            'name': self.user.name,
            'avatar_url': self.user.avatar_url,
            'role': self.role,
            'social_links': self.social_links if self.display_on_certificate else {}
        }

    def __repr__(self):
        return f'<EventParticipation event={self.event_id} user={self.user_id} role={self.role}>'
