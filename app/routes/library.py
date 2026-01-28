from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Library, Certificate

library_bp = Blueprint('library', __name__, url_prefix='/library')


@library_bp.route('/')
@login_required
def view_library():
    # Get filter parameters
    role_filter = request.args.get('role', '')
    category_filter = request.args.get('category', '')

    query = Library.query.filter_by(user_id=current_user.id)\
        .join(Certificate, Library.certificate_id == Certificate.id)

    if role_filter:
        query = query.filter(Certificate.role == role_filter)

    if category_filter:
        query = query.filter(Certificate.metadata_json.like(f'%"{category_filter}"%'))

    library_items = query.order_by(Library.saved_at.desc()).all()

    # Get available filters from user's library
    all_items = Library.query.filter_by(user_id=current_user.id)\
        .join(Certificate, Library.certificate_id == Certificate.id).all()

    roles = sorted(set(item.certificate.role for item in all_items if item.certificate.role))
    categories = set()
    for item in all_items:
        meta = item.certificate.cert_metadata
        if meta and meta.get('category'):
            categories.add(meta['category'])
    categories = sorted(categories)

    # Stats
    stats = {
        'total': len(all_items),
        'own': sum(1 for item in all_items if item.certificate.user_id == current_user.id),
        'saved': sum(1 for item in all_items if item.certificate.user_id != current_user.id),
    }

    return render_template('library/view.html',
                           library_items=library_items,
                           roles=roles,
                           categories=categories,
                           stats=stats,
                           current_role=role_filter,
                           current_category=category_filter)


@library_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def remove_from_library(item_id):
    library_item = Library.query.get_or_404(item_id)

    if library_item.user_id != current_user.id:
        flash('You cannot remove items from another user\'s library.', 'error')
        return redirect(url_for('library.view_library'))

    db.session.delete(library_item)
    db.session.commit()

    flash('Removed from library.', 'info')
    return redirect(url_for('library.view_library'))
