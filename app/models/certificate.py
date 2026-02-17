from datetime import datetime
import secrets
import json
import uuid

from flask import current_app
from app import db


class Certificate(db.Model):
    """
    Core entity for MIKOL - represents knowledge participation certification.
    Every event participation generates a certificate that becomes part of
    the user's professional knowledge identity.
    """
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # participant, speaker, organizer, host

    # Knowledge-centric fields
    title = db.Column(db.String(200))  # Can be different from event title
    description = db.Column(db.Text)  # What knowledge was gained

    # Snapshot of participants at time of issuance (JSON)
    organizers_data = db.Column(db.Text)  # JSON: [{"user_id": X, "name": "Y"}]
    speakers_data = db.Column(db.Text)  # JSON: [{"user_id": X, "name": "Y"}]
    knowledge_units_data = db.Column(db.Text)  # JSON: [{"type": "presentation", "url": "..."}]

    # Sharing & visibility
    share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    is_public = db.Column(db.Boolean, default=True)

    # Phase 2: Visibility & Status
    visibility = db.Column(db.String(20), default='public', nullable=False)  # public, unlisted, private
    status = db.Column(db.String(20), default='active', nullable=False)  # active, revoked, flagged
    verification_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_tags = db.Column(db.Text)  # JSON array of user's personal tags
    snapshot_data = db.Column(db.Text)  # JSON snapshot of event data at issuance time

    # Metadata for categorization & filtering
    metadata_json = db.Column(db.Text)  # JSON: {category, skills, tags, location, date}

    # Timestamps
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='unique_certificate_event_user'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.share_token:
            self.share_token = secrets.token_urlsafe(32)
        if not self.verification_hash:
            self.verification_hash = uuid.uuid4().hex
        if not self.visibility:
            self.visibility = 'public'
        if not self.status:
            self.status = 'active'

    # JSON property helpers
    @property
    def organizers(self):
        if self.organizers_data:
            return json.loads(self.organizers_data)
        return []

    @organizers.setter
    def organizers(self, value):
        self.organizers_data = json.dumps(value) if value else None

    @property
    def speakers(self):
        if self.speakers_data:
            return json.loads(self.speakers_data)
        return []

    @speakers.setter
    def speakers(self, value):
        self.speakers_data = json.dumps(value) if value else None

    @property
    def knowledge_units(self):
        if self.knowledge_units_data:
            return json.loads(self.knowledge_units_data)
        return []

    @knowledge_units.setter
    def knowledge_units(self, value):
        self.knowledge_units_data = json.dumps(value) if value else None

    @property
    def cert_metadata(self):
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}

    @cert_metadata.setter
    def cert_metadata(self, value):
        self.metadata_json = json.dumps(value) if value else None

    @property
    def tags(self):
        if self.user_tags:
            return json.loads(self.user_tags)
        return []

    @tags.setter
    def tags(self, value):
        self.user_tags = json.dumps(value) if value else None

    @property
    def snapshot(self):
        if self.snapshot_data:
            return json.loads(self.snapshot_data)
        return {}

    @snapshot.setter
    def snapshot(self, value):
        self.snapshot_data = json.dumps(value) if value else None

    def take_event_snapshot(self):
        """Capture immutable snapshot of event data at issuance time."""
        event = self.event
        self.snapshot = {
            'event_name': event.title,
            'event_date': event.date.isoformat() if event.date else None,
            'organizer': event.organizer.name if event.organizer else None,
            'category': event.category if hasattr(event, 'category') else None,
            'location': event.location if hasattr(event, 'location') else None,
        }

    def generate_verification_url(self):
        """Generate the public verification URL."""
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5001')
        return f"{base_url}/verify/{self.verification_hash}"

    def generate_share_url(self):
        """Generate the public shareable URL for this certificate."""
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        return f"{base_url}/certificates/public/{self.share_token}"

    def to_public_dict(self):
        """Return sanitized data for public view (no sensitive info)."""
        return {
            'id': self.id,
            'title': self.title or self.event.title,
            'description': self.description,
            'role': self.role,
            'role_display': self.get_role_display(),
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'user_name': self.user.name,
            'user_avatar': self.user.avatar_url,
            'event_title': self.event.title,
            'event_date': self.event.date.isoformat() if self.event.date else None,
            'event_location': self.event.location,
            'event_is_online': self.event.is_online,
            'organizers': self.organizers,
            'speakers': self.speakers,
            'knowledge_units': self.knowledge_units,
            'metadata': self.cert_metadata,
            'share_url': self.generate_share_url()
        }

    def get_role_display(self):
        """Return Hebrew display name for role."""
        role_map = {
            'participant': 'משתתף',
            'speaker': 'מרצה',
            'organizer': 'מארגן',
            'host': 'מנחה'
        }
        return role_map.get(self.role, self.role)

    def get_role_badge_color(self):
        """Return badge color class for role."""
        color_map = {
            'participant': 'info',
            'speaker': 'warning',
            'organizer': 'primary',
            'host': 'secondary'
        }
        return color_map.get(self.role, 'info')

    def __repr__(self):
        return f'<Certificate event={self.event_id} user={self.user_id} role={self.role}>'
