"""
Legacy certificate generator - wraps new certificate_service for backwards compatibility.
"""
from app.services.certificate_service import issue_certificates_for_event


def generate_certificates_for_event(event):
    """Generate certificates for all participants of an event."""
    return issue_certificates_for_event(event)
