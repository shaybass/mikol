from datetime import datetime

from app import db


class EventParticipation(db.Model):
    __tablename__ = 'event_participations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # organizer, speaker, participant, host
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Link to issued certificate
    certificate = db.relationship('Certificate', backref='participation', foreign_keys=[certificate_id])

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='unique_event_user'),
    )

    def __repr__(self):
        return f'<EventParticipation event={self.event_id} user={self.user_id} role={self.role}>'
