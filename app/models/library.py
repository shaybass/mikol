from datetime import datetime
import json

from app import db


class Library(db.Model):
    """
    Tracks certificates saved to a user's personal knowledge library.
    Users can save their own certificates and others' public certificates.
    """
    __tablename__ = 'library'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=False)

    # Personal organization
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # Personal notes about this certificate
    tags_json = db.Column(db.Text)  # JSON: ["python", "ai", "workshop"]

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    certificate = db.relationship('Certificate', backref='library_saves')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'certificate_id', name='unique_library_user_cert'),
    )

    @property
    def tags(self):
        if self.tags_json:
            return json.loads(self.tags_json)
        return []

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value) if value else None

    def add_tag(self, tag):
        """Add a tag to this library item."""
        current_tags = self.tags
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = current_tags

    def remove_tag(self, tag):
        """Remove a tag from this library item."""
        current_tags = self.tags
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = current_tags

    def __repr__(self):
        return f'<Library user={self.user_id} cert={self.certificate_id}>'
