from datetime import datetime
from io import BytesIO
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models import Event, EventParticipation, KnowledgeUnit, Activity
from app.services.certificate_generator import generate_certificates_for_event

events_bp = Blueprint('events', __name__, url_prefix='/events')


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    image_url = StringField('Event Image URL', validators=[Optional(), Length(max=500)])
    category = SelectField('Category', choices=[
        ('', '-- Select Category --'),
        ('tech', 'Technology'),
        ('ai', 'AI & Machine Learning'),
        ('product', 'Product & Design'),
        ('leadership', 'Leadership & Management'),
        ('data', 'Data & Analytics'),
        ('career', 'Career Development'),
        ('other', 'Other')
    ], validators=[Optional()])
    knowledge_outcomes_text = TextAreaField('Knowledge Outcomes', validators=[Optional(), Length(max=1000)])
    date = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M',
                              validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=300)])
    is_online = BooleanField('Online Event')
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('published', 'Published')
    ])
    submit = SubmitField('Save Event')


class KnowledgeUnitForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content/Description', validators=[Optional()])
    type = SelectField('Type', choices=[
        ('presentation', 'Presentation'),
        ('notes', 'Notes'),
        ('recording', 'Recording'),
        ('document', 'Document')
    ])
    url = StringField('URL', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Add Knowledge Unit')


@events_bp.route('/')
def list_events():
    status_filter = request.args.get('status', 'published')
    if status_filter == 'all' and current_user.is_authenticated:
        events = Event.query.order_by(Event.date.desc()).all()
    else:
        events = Event.query.filter_by(status='published').order_by(Event.date.desc()).all()
    return render_template('events/list.html', events=events, status_filter=status_filter)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            image_url=form.image_url.data or None,
            date=form.date.data,
            location=form.location.data,
            is_online=form.is_online.data,
            status=form.status.data,
            category=form.category.data or None,
            organizer_id=current_user.id
        )
        # Parse knowledge outcomes (one per line)
        outcomes_text = form.knowledge_outcomes_text.data
        if outcomes_text:
            event.knowledge_outcomes = [
                line.strip() for line in outcomes_text.strip().split('\n') if line.strip()
            ]

        db.session.add(event)
        db.session.flush()

        # Add organizer as participant
        participation = EventParticipation(
            event_id=event.id,
            user_id=current_user.id,
            role='organizer'
        )
        db.session.add(participation)

        # Log activity
        Activity.log_activity(
            user_id=current_user.id,
            activity_type='created_event',
            content={'event_id': event.id, 'event_title': event.title}
        )

        db.session.commit()

        flash('Knowledge event created successfully!', 'success')
        return redirect(url_for('events.view_event', event_id=event.id))

    return render_template('events/create.html', form=form)


@events_bp.route('/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    participants = event.get_participants_by_role()
    knowledge_units = event.knowledge_units.all()

    user_participation = None
    if current_user.is_authenticated:
        user_participation = event.user_participation(current_user.id)

    return render_template('events/view.html',
                           event=event,
                           participants=participants,
                           knowledge_units=knowledge_units,
                           user_participation=user_participation)


@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        abort(403)

    form = EventForm(obj=event)

    # Pre-populate knowledge outcomes
    if request.method == 'GET' and event.knowledge_outcomes:
        form.knowledge_outcomes_text.data = '\n'.join(event.knowledge_outcomes)

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.image_url = form.image_url.data or None
        event.date = form.date.data
        event.location = form.location.data
        event.is_online = form.is_online.data
        event.status = form.status.data
        event.category = form.category.data or None

        # Parse knowledge outcomes
        outcomes_text = form.knowledge_outcomes_text.data
        if outcomes_text:
            event.knowledge_outcomes = [
                line.strip() for line in outcomes_text.strip().split('\n') if line.strip()
            ]
        else:
            event.knowledge_outcomes = []

        db.session.commit()

        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view_event', event_id=event.id))

    return render_template('events/edit.html', form=form, event=event)


@events_bp.route('/<int:event_id>/join', methods=['POST'])
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.user_participation(current_user.id):
        flash('You have already joined this event.', 'info')
        return redirect(url_for('events.view_event', event_id=event_id))

    role = request.form.get('role', 'participant')
    if role not in ['participant', 'speaker', 'host']:
        role = 'participant'

    participation = EventParticipation(
        event_id=event_id,
        user_id=current_user.id,
        role=role
    )
    db.session.add(participation)
    db.session.commit()

    flash(f'You have joined as {role}!', 'success')
    return redirect(url_for('events.view_event', event_id=event_id))


@events_bp.route('/<int:event_id>/leave', methods=['POST'])
@login_required
def leave_event(event_id):
    event = Event.query.get_or_404(event_id)
    participation = event.user_participation(current_user.id)

    if not participation:
        flash('You are not a participant of this event.', 'info')
        return redirect(url_for('events.view_event', event_id=event_id))

    if participation.role == 'organizer':
        flash('Organizers cannot leave their own event.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))

    db.session.delete(participation)
    db.session.commit()

    flash('You have left the event.', 'info')
    return redirect(url_for('events.view_event', event_id=event_id))


@events_bp.route('/<int:event_id>/complete', methods=['POST'])
@login_required
def complete_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.organizer_id != current_user.id:
        abort(403)

    if event.status == 'completed':
        flash('Event is already completed.', 'info')
        return redirect(url_for('events.view_event', event_id=event_id))

    event.status = 'completed'

    # Generate certificates for all participants
    certificates_created = generate_certificates_for_event(event)

    db.session.commit()

    flash(f'Event completed! {certificates_created} certificates generated.', 'success')
    return redirect(url_for('events.view_event', event_id=event_id))


@events_bp.route('/<int:event_id>/knowledge', methods=['GET', 'POST'])
@login_required
def add_knowledge_unit(event_id):
    event = Event.query.get_or_404(event_id)
    participation = event.user_participation(current_user.id)

    if not participation or participation.role not in ['organizer', 'speaker']:
        flash('Only organizers and speakers can add knowledge units.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))

    form = KnowledgeUnitForm()
    if form.validate_on_submit():
        ku = KnowledgeUnit(
            event_id=event_id,
            author_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            type=form.type.data,
            url=form.url.data
        )
        db.session.add(ku)
        db.session.commit()

        flash('Knowledge unit added!', 'success')
        return redirect(url_for('events.view_event', event_id=event_id))

    return render_template('events/add_knowledge.html', form=form, event=event)


@events_bp.route('/<int:event_id>/qr')
def event_qr(event_id):
    """Show QR code page for event"""
    event = Event.query.get_or_404(event_id)
    return render_template('events/qr.html', event=event)


@events_bp.route('/<int:event_id>/qr.png')
def event_qr_image(event_id):
    """Generate and return QR code image for event"""
    import qrcode
    from PIL import Image

    event = Event.query.get_or_404(event_id)

    # Generate QR code with event URL
    event_url = url_for('events.view_event', event_id=event_id, _external=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(event_url)
    qr.make(fit=True)

    # Create QR code image with MIKOL colors
    img = qr.make_image(fill_color='#2B2D5B', back_color='white')

    # Save to bytes
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png', as_attachment=False)
