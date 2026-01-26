"""Quote Blueprint - Create and Print Quotations"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ProductQuote
from app.forms import SearchForm
from datetime import datetime, date
from sqlalchemy import or_
import json

quote_bp = Blueprint('quote', __name__, url_prefix='/quote')

@quote_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_quote():
    """Create Quote page"""
    search_form = SearchForm()
    
    if request.method == 'POST':
        # Handle form submission
        customer_data = {
            'ref_number': request.form.get('ref_number'),
            'date': request.form.get('date'),
            'customer_name': request.form.get('customer_name'),
            'designation': request.form.get('designation'),
            'organization': request.form.get('organization'),
            'address': request.form.get('address')
        }
        
        # Get products from form
        products_json = request.form.get('products_json')
        if products_json:
            products = json.loads(products_json)
            
            # Store in session for print view
            session['quote_data'] = {
                'customer': customer_data,
                'products': products,
                'created_at': datetime.now().isoformat()
            }
            
            return redirect(url_for('quote.print_quote'))
        else:
            flash('Please add at least one product to the quote.', 'warning')
    
    return render_template('quote/create.html', search_form=search_form)


@quote_bp.route('/search-products')
@login_required
def search_products():
    """AJAX endpoint for product search"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'products': []})
    
    # Search in ProductQuote
    if current_user.is_admin:
        quotes = ProductQuote.query.filter(
            or_(
                ProductQuote.item_name.ilike(f'%{query}%'),
                ProductQuote.cas_no.ilike(f'%{query}%'),
                ProductQuote.cat_no.ilike(f'%{query}%'),
                ProductQuote.make_brand.ilike(f'%{query}%')
            )
        ).limit(20).all()
    else:
        quotes = ProductQuote.query.filter(
            ProductQuote.is_private == False
        ).filter(
            or_(
                ProductQuote.item_name.ilike(f'%{query}%'),
                ProductQuote.cas_no.ilike(f'%{query}%'),
                ProductQuote.cat_no.ilike(f'%{query}%'),
                ProductQuote.make_brand.ilike(f'%{query}%')
            )
        ).limit(20).all()
    
    products = []
    for quote in quotes:
        products.append({
            'id': quote.id,
            'item_name': quote.item_name,
            'make_brand': quote.make_brand,
            'cat_no': quote.cat_no or '',
            'cas_no': quote.cas_no or '',
            'rate': quote.base_price,
            'unit': 'Unit',  # Default, can be customized
            'gst_percent': quote.gst_percent / 100 if quote.gst_percent else 0.18
        })
    
    return jsonify({'products': products})


@quote_bp.route('/print')
@login_required
def print_quote():
    """Print/PDF view of the quote"""
    quote_data = session.get('quote_data')
    if not quote_data:
        flash('No quote data found. Please create a new quote.', 'warning')
        return redirect(url_for('quote.create_quote'))
    
    return render_template('quote/print.html', 
                         customer=quote_data['customer'],
                         products=quote_data['products'])
