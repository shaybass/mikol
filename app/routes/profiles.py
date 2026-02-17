from collections import Counter

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models import User, Certificate, Activity, Event

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
    language = SelectField('Language', choices=[('he', 'עברית'), ('en', 'English')], default='he')
    submit = SubmitField('Save Profile')


@profiles_bp.route('/<int:user_id>')
def view_profile(user_id):
    user = User.query.get_or_404(user_id)

    # Query params for filtering
    filter_category = request.args.get('category')
    filter_year = request.args.get('year', type=int)
    filter_role = request.args.get('role')
    report_view = request.args.get('view') == 'report'

    # All certificates (for total count stat — includes private)
    all_certs = Certificate.query.filter_by(user_id=user_id).all()
    total_events = len(all_certs)

    # Build breakdowns from ALL certs
    category_counter = Counter()
    year_counter = Counter()
    role_counter = Counter()
    category_map = {
        'tech': 'טכנולוגיה', 'business': 'עסקים', 'design': 'עיצוב',
        'marketing': 'שיווק', 'product': 'מוצר', 'data': 'דאטה',
        'ai': 'בינה מלאכותית', 'leadership': 'מנהיגות', 'other': 'אחר'
    }
    role_map = {'organizer': 'מארגן', 'speaker': 'מרצה', 'host': 'מנחה', 'participant': 'משתתף'}

    for cert in all_certs:
        meta = cert.cert_metadata or {}
        cat = meta.get('category')
        if cat:
            category_counter[category_map.get(cat, cat)] += 1
        if cert.event and cert.event.date:
            year_counter[cert.event.date.year] += 1
        role_counter[role_map.get(cert.role, cert.role)] += 1

    # Public certificates only (for display list), with filters
    public_certs = Certificate.query.filter_by(user_id=user_id, visibility='public')\
        .order_by(Certificate.issued_at.desc()).all()

    # Apply filters
    if filter_category:
        public_certs = [c for c in public_certs if (c.cert_metadata or {}).get('category') == filter_category
                        or category_map.get((c.cert_metadata or {}).get('category')) == filter_category]
    if filter_year:
        public_certs = [c for c in public_certs if c.event and c.event.date and c.event.date.year == filter_year]
    if filter_role:
        public_certs = [c for c in public_certs if c.role == filter_role]

    template = 'profiles/view_report.html' if report_view else 'profiles/view.html'

    return render_template(template,
                           profile_user=user,
                           total_events=total_events,
                           category_breakdown=category_counter.most_common(),
                           year_breakdown=sorted(year_counter.items(), reverse=True),
                           role_breakdown=role_counter.most_common(),
                           public_certs=public_certs,
                           filter_category=filter_category,
                           filter_year=filter_year,
                           filter_role=filter_role)


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
        current_user.language = form.language.data

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


    # Follow route removed for MVP
