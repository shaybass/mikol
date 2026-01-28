from datetime import datetime

from app import db


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_relations')
    following = db.relationship('User', foreign_keys=[following_id], backref='follower_relations')

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
    )

    def __repr__(self):
        return f'<Follow {self.follower_id} -> {self.following_id}>'
