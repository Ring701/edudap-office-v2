"""Dashboard Blueprint"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from app.forms import SearchForm, QuoteUploadForm
from app.utils import process_uploaded_file, get_price_intelligence, get_motivational_quote
import os

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    search_form = SearchForm()
    upload_form = QuoteUploadForm()
    
    query = request.args.get('query', '').strip()
    price_data = get_price_intelligence(query=query, user_is_admin=current_user.is_admin)
    quote = get_motivational_quote()
    
    # FIX: Explicitly points to dashboard/index.html
    return render_template('dashboard/index.html',
                         search_form=search_form,
                         upload_form=upload_form,
                         price_data=price_data,
                         query=query,
                         motivational_quote=quote,
                         user=current_user)

@dashboard_bp.route('/upload-quote', methods=['POST'])
@login_required
def upload_quote():
    form = QuoteUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        saved, errors = process_uploaded_file(file, current_user.id, current_user.is_admin)
        if saved:
            flash(f'Success! {len(saved)} products added.', 'success')
        if errors:
            # Show first error only to avoid clutter
            flash(f'Note: {errors[0]}', 'warning')
    else:
        flash('Invalid file.', 'danger')
    return redirect(url_for('dashboard.dashboard'))

# FIX: Added Missing Download Route for the "View" button
@dashboard_bp.route('/download/<path:filename>')
@login_required
def download_file(filename):
    try:
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes')
        return send_from_directory(upload_dir, filename, as_attachment=False)
    except Exception as e:
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.args.get('query', '').strip()
    return redirect(url_for('dashboard.dashboard', query=query))
