"""Dashboard Blueprint - Smart Search & Price Intelligence"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.forms import SearchForm, QuoteUploadForm
from app.utils import process_uploaded_file, get_price_intelligence, get_motivational_quote
from werkzeug.utils import secure_filename

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
    
    return render_template('dashboard.html',
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
            flash(f'Successfully processed {len(saved_quotes)} quote(s)!', 'success')
        if errors:
            for error in errors:
                flash(f'Error: {error}', 'warning')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """AJAX search endpoint"""
    form = SearchForm()
    query = request.args.get('query', '').strip() or request.form.get('query', '').strip()
    
    price_data = get_price_intelligence(query=query, user_is_admin=current_user.is_admin)
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'data': price_data,
            'count': len(price_data)
        })
    
    return redirect(url_for('dashboard.dashboard', query=query))
