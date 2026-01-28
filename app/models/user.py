from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)  # Nullable for OAuth users
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    areas_of_interest = db.Column(db.Text)
    value_proposition = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    cover_url = db.Column(db.String(500))
    google_id = db.Column(db.String(100), unique=True, nullable=True)

    # Knowledge identity fields
    professional_title = db.Column(db.String(150))  # e.g., "Software Engineer" - one line definition
    activity_area = db.Column(db.String(100))  # e.g., "Tel Aviv, Israel"
    interests_json = db.Column(db.Text)  # JSON: up to 5 interest tags

    # Value proposition (optional section)
    value_proposition_title = db.Column(db.String(100))  # e.g., "Available for consulting"
    show_contact_cta = db.Column(db.Boolean, default=False)  # Show "Contact me" CTA

    # Legacy fields (keeping for backwards compatibility)
    bio_tagline = db.Column(db.String(160))
    areas_of_expertise_json = db.Column(db.Text)
    social_links_json = db.Column(db.Text)

    # Social connections (OAuth tokens)
    linkedin_connected = db.Column(db.Boolean, default=False)
    linkedin_token = db.Column(db.Text)  # Encrypted access token
    twitter_connected = db.Column(db.Boolean, default=False)
    twitter_token = db.Column(db.Text)
    facebook_connected = db.Column(db.Boolean, default=False)
    facebook_token = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    organized_events = db.relationship('Event', backref='organizer', lazy='dynamic',
                                       foreign_keys='Event.organizer_id')
    participations = db.relationship('EventParticipation', backref='user', lazy='dynamic')
    knowledge_units = db.relationship('KnowledgeUnit', backref='author', lazy='dynamic')
    certificates = db.relationship('Certificate', backref='user', lazy='dynamic')
    library_items = db.relationship('Library', backref='user', lazy='dynamic')

    # JSON property helpers
    @property
    def interests(self):
        """Up to 5 interest tags."""
        if self.interests_json:
            return json.loads(self.interests_json)[:5]
        return []

    @interests.setter
    def interests(self, value):
        # Limit to 5 tags
        if value:
            self.interests_json = json.dumps(value[:5])
        else:
            self.interests_json = None

    @property
    def areas_of_expertise(self):
        if self.areas_of_expertise_json:
            return json.loads(self.areas_of_expertise_json)
        return []

    @areas_of_expertise.setter
    def areas_of_expertise(self, value):
        self.areas_of_expertise_json = json.dumps(value) if value else None

    @property
    def connected_networks(self):
        """List of connected social networks."""
        networks = []
        if self.linkedin_connected:
            networks.append('linkedin')
        if self.twitter_connected:
            networks.append('twitter')
        if self.facebook_connected:
            networks.append('facebook')
        return networks

    @property
    def social_links(self):
        if self.social_links_json:
            return json.loads(self.social_links_json)
        return {}

    @social_links.setter
    def social_links(self, value):
        self.social_links_json = json.dumps(value) if value else None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_certificates_by_role(self):
        """Group certificates by role."""
        from app.models.certificate import Certificate
        certs = Certificate.query.filter_by(user_id=self.id).all()
        grouped = {'organizer': [], 'speaker': [], 'participant': [], 'host': []}
        for cert in certs:
            if cert.role in grouped:
                grouped[cert.role].append(cert)
        return grouped

    def get_knowledge_identity(self):
        """
        Build knowledge identity based on certificates.
        Returns dict with role counts, categories, and expertise areas.
        """
        from app.models.certificate import Certificate
        certs = Certificate.query.filter_by(user_id=self.id).all()

        identity = {
            'total_certificates': len(certs),
            'roles': {},
            'categories': {},
            'expertise_areas': set()
        }

        for cert in certs:
            # Count roles
            identity['roles'][cert.role] = identity['roles'].get(cert.role, 0) + 1
            # Count categories
            meta = cert.cert_metadata
            cat = meta.get('category') if meta else None
            if cat:
                identity['categories'][cat] = identity['categories'].get(cat, 0) + 1
            # Collect skills from metadata
            skills = meta.get('skills', []) if meta else []
            identity['expertise_areas'].update(skills)

        # Add user-defined expertise
        if self.areas_of_expertise:
            identity['expertise_areas'].update(self.areas_of_expertise)

        identity['expertise_areas'] = list(identity['expertise_areas'])
        return identity

    def calculate_knowledge_score(self):
        """
        Calculate knowledge score based on certificates.
        Speaker=10, Organizer=8, Host=5, Participant=3
        """
        from app.models.certificate import Certificate
        certs = Certificate.query.filter_by(user_id=self.id).all()

        score_map = {
            'speaker': 10,
            'organizer': 8,
            'host': 5,
            'participant': 3
        }

        return sum(score_map.get(cert.role, 0) for cert in certs)

    @property
    def knowledge_score(self):
        return self.calculate_knowledge_score()

    def is_following(self, user):
        from app.models.follow import Follow
        return Follow.query.filter_by(
            follower_id=self.id,
            following_id=user.id
        ).first() is not None

    def follow(self, user):
        if not self.is_following(user) and self.id != user.id:
            from app.models.follow import Follow
            from app.models.activity import Activity
            follow = Follow(follower_id=self.id, following_id=user.id)
            db.session.add(follow)
            Activity.log_activity(
                self.id, 'followed_user',
                {'user_id': user.id, 'user_name': user.name}
            )
            return True
        return False

    def unfollow(self, user):
        from app.models.follow import Follow
        follow = Follow.query.filter_by(
            follower_id=self.id,
            following_id=user.id
        ).first()
        if follow:
            db.session.delete(follow)
            return True
        return False

    @property
    def followers_count(self):
        from app.models.follow import Follow
        return Follow.query.filter_by(following_id=self.id).count()

    @property
    def following_count(self):
        from app.models.follow import Follow
        return Follow.query.filter_by(follower_id=self.id).count()

    @property
    def certificates_count(self):
        from app.models.certificate import Certificate
        return Certificate.query.filter_by(user_id=self.id).count()

    def get_followers(self, limit=None):
        from app.models.follow import Follow
        query = Follow.query.filter_by(following_id=self.id).order_by(Follow.created_at.desc())
        if limit:
            query = query.limit(limit)
        return [f.follower for f in query.all()]

    def get_following(self, limit=None):
        from app.models.follow import Follow
        query = Follow.query.filter_by(follower_id=self.id).order_by(Follow.created_at.desc())
        if limit:
            query = query.limit(limit)
        return [f.following for f in query.all()]

    def get_feed_activities(self, limit=20, offset=0):
        from app.models.follow import Follow
        from app.models.activity import Activity

        following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=self.id).all()]
        if not following_ids:
            return []

        return Activity.query.filter(
            Activity.user_id.in_(following_ids)
        ).order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()

    def __repr__(self):
        return f'<User {self.email}>'
