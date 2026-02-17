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
    venue_name = StringField('Venue/Host Name', validators=[Optional(), Length(max=200)])
    venue_url = StringField('Venue Website/Social', validators=[Optional(), Length(max=500)])
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
            venue_name=form.venue_name.data or None,
            venue_url=form.venue_url.data or None,
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
        event.venue_name = form.venue_name.data or None
        event.venue_url = form.venue_url.data or None

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


@events_bp.route('/<int:event_id>/toggle-collection', methods=['POST'])
@login_required
def toggle_collection(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        abort(403)

    if event.collection_open:
        event.collection_open = False
    else:
        event.collection_open = True
        event.collection_opened_at = datetime.utcnow()

    db.session.commit()

    status = 'open' if event.collection_open else 'closed'
    flash(f'Collection {status}!', 'success')
    return redirect(url_for('events.view_event', event_id=event.id))


@events_bp.route('/<int:event_id>/collection-qr.png')
def collection_qr_image(event_id):
    """Generate QR code for collection URL."""
    import qrcode
    event = Event.query.get_or_404(event_id)

    collect_url = request.host_url.rstrip('/') + f'/collect/{event.collection_code}'

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(collect_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#242650', back_color='white')

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=False)


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


@events_bp.route('/<int:event_id>/agenda', methods=['GET', 'POST'])
@login_required
def manage_agenda(event_id):
    """Manage event agenda - add/edit agenda items"""
    event = Event.query.get_or_404(event_id)
    participation = event.user_participation(current_user.id)

    if not participation or participation.role != 'organizer':
        flash('Only organizers can manage the agenda.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))

    if request.method == 'POST':
        # Get agenda data from form
        agenda_items = []
        times = request.form.getlist('time[]')
        titles = request.form.getlist('agenda_title[]')
        descriptions = request.form.getlist('agenda_description[]')
        speaker_ids = request.form.getlist('speaker_id[]')

        for i in range(len(times)):
            if times[i] and titles[i]:
                item = {
                    'time': times[i],
                    'title': titles[i],
                    'description': descriptions[i] if i < len(descriptions) else '',
                    'speaker_id': int(speaker_ids[i]) if i < len(speaker_ids) and speaker_ids[i] else None
                }
                agenda_items.append(item)

        event.agenda = agenda_items
        db.session.commit()

        flash('Agenda updated!', 'success')
        return redirect(url_for('events.view_event', event_id=event_id))

    # Get speakers for dropdown
    participants = event.get_participants_by_role()
    speakers = participants.get('speaker', [])

    return render_template('events/agenda.html',
                           event=event,
                           speakers=speakers)


@events_bp.route('/<int:event_id>/my-profile', methods=['GET', 'POST'])
@login_required
def update_participation_profile(event_id):
    """Update participant's social links for this event (self-tagging)"""
    event = Event.query.get_or_404(event_id)
    participation = event.user_participation(current_user.id)

    if not participation:
        flash('You are not a participant of this event.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))

    if request.method == 'POST':
        # Get social links from form
        social_links = {}
        if request.form.get('linkedin'):
            social_links['linkedin'] = request.form.get('linkedin')
        if request.form.get('twitter'):
            social_links['twitter'] = request.form.get('twitter')
        if request.form.get('instagram'):
            social_links['instagram'] = request.form.get('instagram')
        if request.form.get('website'):
            social_links['website'] = request.form.get('website')

        participation.social_links = social_links
        participation.display_on_certificate = request.form.get('display_on_certificate') == 'on'

        db.session.commit()

        flash('Your profile for this event has been updated!', 'success')
        return redirect(url_for('events.view_event', event_id=event_id))

    return render_template('events/participation_profile.html',
                           event=event,
                           participation=participation)
