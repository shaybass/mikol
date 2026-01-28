from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.models import Event

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')


@scan_bp.route('/')
@login_required
def scan_page():
    """QR code scanner page"""
    return render_template('scan/scan_page.html')


@scan_bp.route('/process', methods=['POST'])
@login_required
def process_scan():
    """Process scanned QR code data"""
    data = request.get_json()
    qr_data = data.get('qr_data', '')

    # QR data should be in format: mikol:event:{event_id}
    if qr_data.startswith('mikol:event:'):
        try:
            event_id = int(qr_data.replace('mikol:event:', ''))
            event = Event.query.get(event_id)
            if event:
                return jsonify({
                    'success': True,
                    'type': 'event',
                    'redirect_url': url_for('events.view_event', event_id=event_id)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Event not found'
                })
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid QR code format'
            })

    # Handle URL-based QR codes
    if 'mikol' in qr_data.lower() or request.host in qr_data:
        return jsonify({
            'success': True,
            'type': 'url',
            'redirect_url': qr_data
        })

    return jsonify({
        'success': False,
        'error': 'Unrecognized QR code'
    })
