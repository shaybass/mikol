from datetime import datetime
import json

from app import db


class Event(db.Model):
    """
    Knowledge event - the source of certificates.
    Each event generates certificates for all participants upon completion.
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(300))
    is_online = db.Column(db.Boolean, default=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, published, completed

    # Visual & Knowledge fields
    image_url = db.Column(db.String(500))  # Event cover/visual image
    category = db.Column(db.String(50))  # Tech, Business, Design, Marketing, etc.
    knowledge_outcomes_json = db.Column(db.Text)  # JSON: ["Learn X", "Understand Y", "Build Z"]
    content_links_json = db.Column(db.Text)  # JSON: [{"type": "slides", "url": "...", "title": "..."}]

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participations = db.relationship('EventParticipation', backref='event', lazy='dynamic',
                                     cascade='all, delete-orphan')
    knowledge_units = db.relationship('KnowledgeUnit', backref='event', lazy='dynamic',
                                      cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='event', lazy='dynamic',
                                   cascade='all, delete-orphan')

    # JSON property helpers
    @property
    def knowledge_outcomes(self):
        if self.knowledge_outcomes_json:
            return json.loads(self.knowledge_outcomes_json)
        return []

    @knowledge_outcomes.setter
    def knowledge_outcomes(self, value):
        self.knowledge_outcomes_json = json.dumps(value) if value else None

    @property
    def content_links(self):
        if self.content_links_json:
            return json.loads(self.content_links_json)
        return []

    @content_links.setter
    def content_links(self, value):
        self.content_links_json = json.dumps(value) if value else None

    def get_participants_by_role(self):
        """Get participants grouped by role."""
        from app.models.participation import EventParticipation
        participations = EventParticipation.query.filter_by(event_id=self.id).all()
        grouped = {'organizer': [], 'speaker': [], 'participant': [], 'host': []}
        for p in participations:
            if p.role in grouped:
                grouped[p.role].append(p.user)
        return grouped

    def user_participation(self, user_id):
        """Get user's participation in this event."""
        from app.models.participation import EventParticipation
        return EventParticipation.query.filter_by(
            event_id=self.id, user_id=user_id
        ).first()

    def get_organizers_json(self):
        """Get organizers as JSON-serializable list for certificate snapshot."""
        participants = self.get_participants_by_role()
        return [
            {'user_id': u.id, 'name': u.name, 'avatar_url': u.avatar_url}
            for u in participants.get('organizer', [])
        ]

    def get_speakers_json(self):
        """Get speakers as JSON-serializable list for certificate snapshot."""
        participants = self.get_participants_by_role()
        return [
            {'user_id': u.id, 'name': u.name, 'avatar_url': u.avatar_url}
            for u in participants.get('speaker', [])
        ]

    def get_knowledge_units_json(self):
        """Get knowledge units as JSON-serializable list for certificate."""
        units = self.knowledge_units.all()
        return [
            {
                'type': ku.type,
                'title': ku.title,
                'url': ku.url,
                'content': ku.content
            }
            for ku in units
        ]

    def issue_certificate(self, user_id, role):
        """
        Issue a certificate for a user's participation in this event.
        Returns existing certificate if already issued.
        """
        from app.models.certificate import Certificate

        # Check if certificate already exists
        existing = Certificate.query.filter_by(
            event_id=self.id,
            user_id=user_id
        ).first()

        if existing:
            return existing

        # Create new certificate with full knowledge snapshot
        cert = Certificate(
            event_id=self.id,
            user_id=user_id,
            role=role,
            title=self.title,
            description=self.description,
            organizers=self.get_organizers_json(),
            speakers=self.get_speakers_json(),
            knowledge_units=self.get_knowledge_units_json(),
            is_public=True,
            cert_metadata={
                'category': self.category,
                'date': self.date.isoformat() if self.date else None,
                'location': self.location,
                'is_online': self.is_online,
                'knowledge_outcomes': self.knowledge_outcomes
            }
        )

        db.session.add(cert)
        return cert

    def get_certificates(self):
        """Get all certificates issued for this event."""
        return self.certificates.all()

    def get_category_display(self):
        """Return Hebrew display name for category."""
        category_map = {
            'tech': 'טכנולוגיה',
            'business': 'עסקים',
            'design': 'עיצוב',
            'marketing': 'שיווק',
            'product': 'מוצר',
            'data': 'דאטה',
            'ai': 'בינה מלאכותית',
            'leadership': 'מנהיגות',
            'other': 'אחר'
        }
        return category_map.get(self.category, self.category or 'כללי')

    def __repr__(self):
        return f'<Event {self.title}>'
