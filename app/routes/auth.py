from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app import db, oauth
from app.models import User, Activity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    form = LoginForm()
    google_enabled = bool(current_app.config.get('GOOGLE_CLIENT_ID'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page or url_for('dashboard.dashboard'))
        flash('Invalid email or password.', 'error')

    return render_template('auth/login.html', form=form, google_enabled=google_enabled)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    form = RegisterForm()
    google_enabled = bool(current_app.config.get('GOOGLE_CLIENT_ID'))

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # Log activity for joining MIKOL
        Activity.log_activity(
            user_id=user.id,
            activity_type='joined_mikol',
            content={}
        )

        db.session.commit()

        login_user(user)
        flash('Registration successful! Welcome to MIKOL.', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.dashboard'))

    return render_template('auth/register.html', form=form, google_enabled=google_enabled)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login."""
    if not current_app.config.get('GOOGLE_CLIENT_ID'):
        flash('Google login is not configured. Please use email login.', 'info')
        return redirect(url_for('auth.login'))

    google = oauth.create_client('google')
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    if not current_app.config.get('GOOGLE_CLIENT_ID'):
        flash('Google login is not configured.', 'error')
        return redirect(url_for('auth.login'))

    google = oauth.create_client('google')
    try:
        token = google.authorize_access_token()
    except Exception:
        flash('Google authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    user_info = token.get('userinfo')
    if not user_info:
        user_info = google.userinfo()

    email = user_info.get('email', '').lower()
    name = user_info.get('name', '')
    avatar_url = user_info.get('picture', '')

    if not email:
        flash('Could not retrieve email from Google. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    # Find or create user
    user = User.query.filter_by(email=email).first()
    if user:
        # Update avatar if not set
        if not user.avatar_url and avatar_url:
            user.avatar_url = avatar_url
            db.session.commit()
    else:
        # Create new user
        user = User(
            name=name,
            email=email,
            avatar_url=avatar_url
        )
        # Set a random password (user logs in via Google)
        import secrets
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.flush()

        Activity.log_activity(
            user_id=user.id,
            activity_type='joined_mikol',
            content={}
        )
        db.session.commit()
        flash('Welcome to MIKOL! Your account has been created.', 'success')

    login_user(user)
    next_page = request.args.get('next')
    return redirect(next_page or url_for('dashboard.dashboard'))
