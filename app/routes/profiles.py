from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models import User, Certificate, Activity

profiles_bp = Blueprint('profiles', __name__, url_prefix='/profiles')


class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    professional_title = StringField('Professional Definition', validators=[Optional(), Length(max=150)])
    activity_area = StringField('Activity Area', validators=[Optional(), Length(max=100)])
    interests_text = StringField('Interests', validators=[Optional(), Length(max=200)])
    avatar_url = StringField('Profile Picture URL', validators=[Optional(), Length(max=500)])
    cover_url = StringField('Cover Image URL', validators=[Optional(), Length(max=500)])
    # Value proposition section
    value_proposition_title = StringField('Value Proposition Title', validators=[Optional(), Length(max=100)])
    value_proposition = TextAreaField('Value Proposition', validators=[Optional(), Length(max=500)])
    show_contact_cta = BooleanField('Show "Contact me" button')
    submit = SubmitField('Save Profile')


@profiles_bp.route('/<int:user_id>')
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    certificates_by_role = user.get_certificates_by_role()

    # Group certificates by organizer
    certificates_by_organizer = {}
    all_certs = Certificate.query.filter_by(user_id=user_id).all()
    for cert in all_certs:
        organizer = cert.event.organizer
        if organizer.id not in certificates_by_organizer:
            certificates_by_organizer[organizer.id] = {
                'organizer': organizer,
                'certificates': []
            }
        certificates_by_organizer[organizer.id]['certificates'].append(cert)

    # Check if current user is following this profile
    is_following = False
    if current_user.is_authenticated and current_user.id != user_id:
        is_following = current_user.is_following(user)

    # Get user activities
    activities = Activity.query.filter_by(user_id=user_id)\
        .order_by(Activity.created_at.desc()).limit(20).all()

    return render_template('profiles/view.html',
                           profile_user=user,
                           certificates_by_role=certificates_by_role,
                           certificates_by_organizer=certificates_by_organizer,
                           is_following=is_following,
                           activities=activities)


@profiles_bp.route('/<int:user_id>/certificates')
def user_certificates(user_id):
    user = User.query.get_or_404(user_id)
    certificates = Certificate.query.filter_by(user_id=user_id)\
        .order_by(Certificate.issued_at.desc()).all()
    return render_template('profiles/certificates.html',
                           profile_user=user,
                           certificates=certificates)


@profiles_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)

    # Pre-populate interests field
    if request.method == 'GET' and current_user.interests:
        form.interests_text.data = ', '.join(current_user.interests)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.professional_title = form.professional_title.data
        current_user.activity_area = form.activity_area.data
        current_user.avatar_url = form.avatar_url.data
        current_user.cover_url = form.cover_url.data
        current_user.value_proposition_title = form.value_proposition_title.data
        current_user.value_proposition = form.value_proposition.data
        current_user.show_contact_cta = form.show_contact_cta.data

        # Parse interests from comma-separated text (max 5)
        interests_text = form.interests_text.data
        if interests_text:
            current_user.interests = [
                s.strip() for s in interests_text.split(',') if s.strip()
            ][:5]
        else:
            current_user.interests = []

        db.session.commit()

        flash('Profile updated!', 'success')
        return redirect(url_for('profiles.view_profile', user_id=current_user.id))

    return render_template('profiles/edit.html', form=form)


@profiles_bp.route('/<int:user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
    """Toggle follow/unfollow a user"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return jsonify({'error': 'Cannot follow yourself'}), 400

    if current_user.is_following(user):
        current_user.unfollow(user)
        action = 'unfollowed'
        is_following = False
    else:
        current_user.follow(user)
        action = 'followed'
        is_following = True
        # Log activity
        Activity.log_activity(
            user_id=current_user.id,
            activity_type='followed_user',
            content={'user_id': user.id, 'user_name': user.name}
        )

    db.session.commit()

    return jsonify({
        'action': action,
        'is_following': is_following,
        'followers_count': user.followers_count
    })
