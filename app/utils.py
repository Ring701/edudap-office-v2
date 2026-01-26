"""Utility functions for PDF/Excel parsing and price intelligence"""
import os
import re
from datetime import datetime
import pandas as pd
import PyPDF2
from flask import current_app
from app.models import ProductQuote, db

def parse_excel(file_path):
    """Parse Excel file and extract product quote data"""
    quotes = []
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Common column name mappings
        column_mapping = {
            'item_name': ['Item Name', 'Item', 'Product Name', 'Product', 'Name'],
            'cas_no': ['CAS No', 'CAS Number', 'CAS', 'CAS#'],
            'cat_no': ['Cat No', 'Catalog No', 'Cat Number', 'Product No', 'Product Number', 'Cat#'],
            'make_brand': ['Make', 'Brand', 'Manufacturer', 'Company'],
            'base_price': ['Price', 'Base Price', 'Cost', 'Amount'],
            'gst_percent': ['GST', 'GST %', 'Tax', 'Tax %'],
            'specifications': ['Specifications', 'Specs', 'Description', 'Details']
        }
        
        # Find actual column names
        actual_columns = {}
        for key, possible_names in column_mapping.items():
            for col in df.columns:
                if any(name.lower() in str(col).lower() for name in possible_names):
                    actual_columns[key] = col
                    break
        
        # Extract data
        for idx, row in df.iterrows():
            try:
                item_name = str(row.get(actual_columns.get('item_name', ''), '')).strip()
                if not item_name or item_name.lower() in ['nan', 'none', '']:
                    continue
                
                quote_data = {
                    'item_name': item_name,
                    'cas_no': str(row.get(actual_columns.get('cas_no', ''), '')).strip() or None,
                    'cat_no': str(row.get(actual_columns.get('cat_no', ''), '')).strip() or None,
                    'make_brand': str(row.get(actual_columns.get('make_brand', ''), 'Unknown')).strip(),
                    'base_price': float(row.get(actual_columns.get('base_price', 0), 0)) or 0.0,
                    'gst_percent': float(row.get(actual_columns.get('gst_percent', 18), 18)) or 18.0,
                    'specifications': str(row.get(actual_columns.get('specifications', ''), '')).strip() or None
                }
                
                if quote_data['base_price'] > 0:
                    quotes.append(quote_data)
            except Exception as e:
                current_app.logger.warning(f"Error parsing row {idx}: {str(e)}")
                continue
                
    except Exception as e:
        current_app.logger.error(f"Error parsing Excel file: {str(e)}")
    
    return quotes


def parse_pdf(file_path):
    """Parse PDF file and extract product quote data"""
    quotes = []
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Extract structured data using regex patterns
            # This is a simplified parser - can be enhanced based on actual PDF format
            lines = text.split('\n')
            current_quote = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extract CAS Number (format: CAS-XXXXX-XX-X)
                cas_match = re.search(r'CAS[:\s-]*(\d{2,7}-\d{2}-\d)', line, re.IGNORECASE)
                if cas_match:
                    current_quote['cas_no'] = cas_match.group(1)
                
                # Extract Catalog Number
                cat_match = re.search(r'(?:Cat|Catalog|Product)[\s#:]*([A-Z0-9\-]+)', line, re.IGNORECASE)
                if cat_match:
                    current_quote['cat_no'] = cat_match.group(1)
                
                # Extract Price (look for currency symbols and numbers)
                price_match = re.search(r'[₹$€£]?\s*(\d+[.,]\d{2})', line)
                if price_match:
                    price_str = price_match.group(1).replace(',', '.')
                    try:
                        current_quote['base_price'] = float(price_str)
                    except:
                        pass
                
                # Extract Brand/Make (usually in uppercase or specific format)
                brand_match = re.search(r'(?:Make|Brand|Manufacturer)[:\s]+([A-Z][A-Za-z0-9\s]+)', line, re.IGNORECASE)
                if brand_match:
                    current_quote['make_brand'] = brand_match.group(1).strip()
            
            # If we found any data, create a quote
            if current_quote and 'base_price' in current_quote:
                # Try to extract item name (usually first significant line)
                item_name = lines[0] if lines else "Unknown Item"
                current_quote['item_name'] = item_name[:200]
                current_quote['make_brand'] = current_quote.get('make_brand', 'Unknown')
                current_quote['gst_percent'] = 18.0  # Default
                quotes.append(current_quote)
                
    except Exception as e:
        current_app.logger.error(f"Error parsing PDF file: {str(e)}")
    
    return quotes


def process_uploaded_file(file, user_id, is_admin):
    """Process uploaded file and create/update ProductQuote records"""
    saved_quotes = []
    errors = []
    
    try:
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes', filename)
        file.save(file_path)
        
        # Parse based on file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        quotes_data = []
        
        if file_ext in ['.xlsx', '.xls']:
            quotes_data = parse_excel(file_path)
        elif file_ext == '.pdf':
            quotes_data = parse_pdf(file_path)
        else:
            errors.append(f"Unsupported file type: {file_ext}")
            return saved_quotes, errors
        
        # Process each quote with deduplication logic
        for quote_data in quotes_data:
            try:
                # Check for existing quote (deduplication)
                existing = ProductQuote.query.filter_by(
                    item_name=quote_data['item_name'],
                    make_brand=quote_data['make_brand'],
                    cas_no=quote_data.get('cas_no') or '',
                    cat_no=quote_data.get('cat_no') or '',
                    base_price=quote_data['base_price']
                ).first()
                
                if existing:
                    # Update existing record
                    existing.specifications = quote_data.get('specifications') or existing.specifications
                    existing.file_url = file_path
                    existing.created_at = datetime.utcnow()
                    saved_quotes.append(existing)
                else:
                    # Create new record
                    new_quote = ProductQuote(
                        item_name=quote_data['item_name'],
                        cas_no=quote_data.get('cas_no'),
                        cat_no=quote_data.get('cat_no'),
                        make_brand=quote_data['make_brand'],
                        base_price=quote_data['base_price'],
                        gst_percent=quote_data.get('gst_percent', 18.0),
                        specifications=quote_data.get('specifications'),
                        file_url=file_path,
                        uploaded_by_id=user_id,
                        is_private=is_admin  # Admin uploads are private
                    )
                    db.session.add(new_quote)
                    saved_quotes.append(new_quote)
                    
            except Exception as e:
                errors.append(f"Error processing quote: {str(e)}")
                current_app.logger.error(f"Error processing quote: {str(e)}")
        
        db.session.commit()
        
    except Exception as e:
        errors.append(f"Error processing file: {str(e)}")
        current_app.logger.error(f"Error processing uploaded file: {str(e)}")
        db.session.rollback()
    
    return saved_quotes, errors


def get_price_intelligence(query=None, user_is_admin=False):
    """Get price intelligence with min/max grouping by brand"""
    # Base query
    if user_is_admin:
        # Admin can see all (private + public)
        base_query = ProductQuote.query
    else:
        # Employees can only see public quotes
        base_query = ProductQuote.query.filter_by(is_private=False)
    
    # Apply search filter
    if query:
        search_term = f"%{query}%"
        base_query = base_query.filter(
            db.or_(
                ProductQuote.item_name.ilike(search_term),
                ProductQuote.cas_no.ilike(search_term),
                ProductQuote.cat_no.ilike(search_term),
                ProductQuote.make_brand.ilike(search_term),
                ProductQuote.specifications.ilike(search_term)
            )
        )
    
    # Get all matching quotes
    all_quotes = base_query.all()
    
    # Group by Item Name + Brand and calculate min/max
    grouped_data = {}
    for quote in all_quotes:
        key = f"{quote.item_name}|{quote.make_brand}"
        if key not in grouped_data:
            grouped_data[key] = {
                'item_name': quote.item_name,
                'make_brand': quote.make_brand,
                'cas_no': quote.cas_no,
                'cat_no': quote.cat_no,
                'prices': [],
                'specifications': quote.specifications,
                'count': 0
            }
        
        grouped_data[key]['prices'].append(quote.base_price)
        grouped_data[key]['count'] += 1
    
    # Calculate min/max for each group
    result = []
    for key, data in grouped_data.items():
        prices = data['prices']
        result.append({
            'item_name': data['item_name'],
            'make_brand': data['make_brand'],
            'cas_no': data['cas_no'],
            'cat_no': data['cat_no'],
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'quote_count': data['count'],
            'specifications': data['specifications']
        })
    
    # Sort by item name
    result.sort(key=lambda x: x['item_name'])
    
    return result


def get_motivational_quote():
    """Return a random motivational quote"""
    quotes = [
        "Success is the sum of small efforts repeated day in and day out.",
        "The only way to do great work is to love what you do.",
        "Innovation distinguishes between a leader and a follower.",
        "Don't be afraid to give up the good to go for the great.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "Excellence is not a skill, it's an attitude.",
        "The harder you work, the luckier you get.",
        "Dream big and dare to fail."
    ]
    import random
    return random.choice(quotes)
