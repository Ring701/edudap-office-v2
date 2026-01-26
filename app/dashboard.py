"""Dashboard Blueprint - Smart Search & Price Intelligence"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import login_required, current_user
from app.forms import SearchForm, QuoteUploadForm
from app.utils import process_uploaded_file, get_price_intelligence, get_motivational_quote
from werkzeug.utils import secure_filename
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

    return render_template('dashboard/index.html', 
                         search_form=search_form,
                         upload_form=upload_form,
                         price_intelligence=price_data,
                         motivational_quote=quote)

@dashboard_bp.route('/upload-quote', methods=['POST'])
@login_required
def upload_quote():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard.dashboard'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard.dashboard'))
        
    if file:
        saved_quotes, errors = process_uploaded_file(file, current_user.id, current_user.is_admin)
        if errors:
            flash(f"Upload completed with issues: {'; '.join(errors)}", 'warning')
        else:
            flash(f"Successfully processed {len(saved_quotes)} products!", 'success')
            
    return redirect(url_for('dashboard.dashboard'))

# --- NEW: ROUTE TO DOWNLOAD FILES ---
@dashboard_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    """Download the original uploaded file"""
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes')
    return send_from_directory(upload_folder, filename)
