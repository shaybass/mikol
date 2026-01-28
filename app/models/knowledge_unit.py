from datetime import datetime

from app import db


class KnowledgeUnit(db.Model):
    __tablename__ = 'knowledge_units'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)  # presentation, notes, recording, document
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<KnowledgeUnit {self.title}>'
