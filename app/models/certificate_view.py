from datetime import datetime

from app import db


class CertificateView(db.Model):
    """
    Tracks views of certificates for analytics.
    Records each time a certificate is viewed (public or authenticated).
    """
    __tablename__ = 'certificate_views'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=False)
    viewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous views

    # View context
    view_type = db.Column(db.String(20), default='public')  # public, direct, qr_scan, social_share
    referrer = db.Column(db.String(500))  # Where the view came from (e.g., linkedin, twitter, direct)
    user_agent = db.Column(db.String(500))  # Browser/device info
    ip_hash = db.Column(db.String(64))  # Hashed IP for unique visitor tracking (privacy-safe)

    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    certificate = db.relationship('Certificate', backref=db.backref('views', lazy='dynamic'))
    viewer = db.relationship('User', backref='certificate_views')

    @staticmethod
    def log_view(certificate_id, viewer_id=None, view_type='public', referrer=None, user_agent=None, ip_hash=None):
        """Log a certificate view."""
        view = CertificateView(
            certificate_id=certificate_id,
            viewer_id=viewer_id,
            view_type=view_type,
            referrer=referrer,
            user_agent=user_agent,
            ip_hash=ip_hash
        )
        db.session.add(view)
        return view

    @staticmethod
    def get_certificate_stats(certificate_id):
        """Get view statistics for a certificate."""
        from sqlalchemy import func

        total_views = CertificateView.query.filter_by(certificate_id=certificate_id).count()
        unique_viewers = db.session.query(func.count(func.distinct(CertificateView.ip_hash)))\
            .filter(CertificateView.certificate_id == certificate_id).scalar() or 0
        authenticated_views = CertificateView.query.filter_by(
            certificate_id=certificate_id
        ).filter(CertificateView.viewer_id.isnot(None)).count()

        # Views by source
        views_by_source = db.session.query(
            CertificateView.view_type,
            func.count(CertificateView.id)
        ).filter(
            CertificateView.certificate_id == certificate_id
        ).group_by(CertificateView.view_type).all()

        return {
            'total_views': total_views,
            'unique_viewers': unique_viewers,
            'authenticated_views': authenticated_views,
            'anonymous_views': total_views - authenticated_views,
            'views_by_source': dict(views_by_source)
        }

    def __repr__(self):
        return f'<CertificateView cert={self.certificate_id} viewer={self.viewer_id}>'
