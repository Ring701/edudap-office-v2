"""Dashboard Blueprint - Smart Search & Price Intelligence"""
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
    """Main dashboard with Smart Search & Price Intelligence"""
    search_form = SearchForm()
    upload_form = QuoteUploadForm()
    
    # Get search query
    query = request.args.get('query', '').strip()
    
    # Get price intelligence data
    price_data = get_price_intelligence(query=query, user_is_admin=current_user.is_admin)
    
    # Get motivational quote
    quote = get_motivational_quote()
    
    # Explicitly render the file in the dashboard subfolder
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
    """Handle quote file upload"""
    form = QuoteUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        saved_quotes, errors = process_uploaded_file(
            file,
            current_user.id,
            current_user.is_admin
        )
        
        if saved_quotes:
            flash(f'Success! {len(saved_quotes)} products extracted and saved.', 'success')
        
        if errors:
            # Show the first few errors to avoid flooding flash messages
            for error in errors[:3]:
                flash(f'Warning: {error}', 'warning')
            if len(errors) > 3:
                flash(f'And {len(errors)-3} more issues...', 'warning')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    """Serve the original uploaded file for viewing/downloading"""
    try:
        # Construct path to upload folder
        uploads = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes')
        return send_from_directory(uploads, filename, as_attachment=False)
    except Exception as e:
        flash(f'Error retrieving file: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search redirect helper"""
    query = request.args.get('query', '').strip() or request.form.get('query', '').strip()
    return redirect(url_for('dashboard.dashboard', query=query))
