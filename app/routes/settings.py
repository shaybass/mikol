from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def settings_index():
    """Main settings page - redirects to social connections."""
    return redirect(url_for('settings.social_connections'))


@settings_bp.route('/social')
@login_required
def social_connections():
    """Social connections settings page."""
    return render_template('settings/social.html')


@settings_bp.route('/social/connect/<network>')
@login_required
def connect_social(network):
    """
    Initiate OAuth connection to a social network.
    Placeholder - in production, this would redirect to OAuth provider.
    """
    valid_networks = ['linkedin', 'twitter', 'facebook']
    if network not in valid_networks:
        flash('Invalid network.', 'error')
        return redirect(url_for('settings.social_connections'))

    # Placeholder: In production, redirect to OAuth provider
    flash(f'{network.title()} connection is not yet configured. Coming soon!', 'info')
    return redirect(url_for('settings.social_connections'))


@settings_bp.route('/social/disconnect/<network>', methods=['POST'])
@login_required
def disconnect_social(network):
    """Disconnect a social network."""
    valid_networks = ['linkedin', 'twitter', 'facebook']
    if network not in valid_networks:
        flash('Invalid network.', 'error')
        return redirect(url_for('settings.social_connections'))

    # Update user's connection status
    if network == 'linkedin':
        current_user.linkedin_connected = False
        current_user.linkedin_token = None
    elif network == 'twitter':
        current_user.twitter_connected = False
        current_user.twitter_token = None
    elif network == 'facebook':
        current_user.facebook_connected = False
        current_user.facebook_token = None

    db.session.commit()
    flash(f'{network.title()} disconnected.', 'success')
    return redirect(url_for('settings.social_connections'))


# Placeholder OAuth callbacks - would be implemented with real OAuth
@settings_bp.route('/social/callback/linkedin')
@login_required
def linkedin_callback():
    """LinkedIn OAuth callback - placeholder."""
    # In production: exchange code for token, store token
    current_user.linkedin_connected = True
    current_user.linkedin_token = 'placeholder_token'
    db.session.commit()
    flash('LinkedIn connected!', 'success')
    return redirect(url_for('settings.social_connections'))


@settings_bp.route('/social/callback/twitter')
@login_required
def twitter_callback():
    """Twitter OAuth callback - placeholder."""
    current_user.twitter_connected = True
    current_user.twitter_token = 'placeholder_token'
    db.session.commit()
    flash('Twitter/X connected!', 'success')
    return redirect(url_for('settings.social_connections'))


@settings_bp.route('/social/callback/facebook')
@login_required
def facebook_callback():
    """Facebook OAuth callback - placeholder."""
    current_user.facebook_connected = True
    current_user.facebook_token = 'placeholder_token'
    db.session.commit()
    flash('Facebook connected!', 'success')
    return redirect(url_for('settings.social_connections'))
