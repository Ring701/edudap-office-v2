"""Utility functions for PDF/Excel parsing and price intelligence"""
import os
import re
from datetime import datetime
import pandas as pd
import PyPDF2
from flask import current_app
from app.models import ProductQuote, db
from sqlalchemy import or_

def parse_excel(file_path):
    """Parse Excel file with Nuclear Filtering for Garbage Data"""
    quotes = []
    try:
        # Read file as string first to analyze structure without forcing headers
        df_raw = pd.read_excel(file_path, header=None, engine='openpyxl', dtype=str)
        
        # 1. Dynamic Header Detection
        # We scan the first 20 rows to find where the actual table starts
        header_index = -1
        header_keywords = ['item', 'description', 'particulars', 'product', 'name', 'material']
        
        for idx, row in df_raw.head(20).iterrows():
            row_text = ' '.join([str(v).lower() for v in row.values if pd.notna(v)])
            # If row contains at least one strong keyword
            if any(k in row_text for k in header_keywords):
                header_index = idx
                break
        
        if header_index != -1:
            # Reload dataframe using the found header row
            df = df_raw.iloc[header_index + 1:].copy()
            df.columns = df_raw.iloc[header_index]
        else:
            # Fallback: Assume first row
            df = pd.read_excel(file_path, engine='openpyxl')

        # 2. Smart Column Mapping
        def get_col(candidates):
            for col in df.columns:
                col_str = str(col).lower().strip()
                if any(c in col_str for c in candidates):
                    return col
            return None

        col_item = get_col(['item', 'description', 'product', 'particulars', 'name'])
        col_price = get_col(['price', 'rate', 'amount', 'cost', 'unit price'])
        col_make = get_col(['make', 'brand', 'manufacturer'])
        col_cas = get_col(['cas', 'cas no'])
        col_cat = get_col(['cat', 'catalog', 'cat no'])
        col_spec = get_col(['spec', 'pack', 'specification'])
        
        # If we can't find an item column, we can't process
        if not col_item:
            return []

        # 3. Extract Data with NUCLEAR FILTER
        for idx, row in df.iterrows():
            try:
                # Get Item Name
                item_name = str(row.get(col_item, '')).strip()
                
                # --- NUCLEAR FILTER START ---
                # 1. Ignore empty or NaN
                if not item_name or item_name.lower() in ['nan', 'none', 'nat']:
                    continue
                
                # 2. Ignore pure numbers (e.g., "1", "10", "100")
                if item_name.isdigit():
                    continue
                    
                # 3. Ignore Serial Number patterns (e.g., "1.", "1.0", "10)")
                if re.match(r'^\d+[.)]?$', item_name):
                    continue
                
                # 4. Ignore tiny strings (likely noise)
                if len(item_name) < 3:
                    continue
                
                # 5. Stop words that indicate footer
                if any(x in item_name.lower() for x in ['total', 'terms', 'signature', 'amount in words', 'page']):
                    break
                # --- NUCLEAR FILTER END ---

                # Get Price
                raw_price = str(row.get(col_price, 0)) if col_price else '0'
                # Clean price: remove currency symbols, commas, keep digits and dot
                clean_price = re.sub(r'[^\d.]', '', raw_price)
                try: 
                    price = float(clean_price)
                except: 
                    price = 0.0

                if price > 0:
                    quotes.append({
                        'item_name': item_name,
                        'base_price': price,
                        'make_brand': str(row.get(col_make, 'Unknown')).strip() if col_make else 'Unknown',
                        'cas_no': str(row.get(col_cas, '')).strip() if col_cas else None,
                        'cat_no': str(row.get(col_cat, '')).strip() if col_cat else None,
                        'specifications': str(row.get(col_spec, '')).strip() if col_spec else None
                    })
            except Exception:
                continue
            
    except Exception as e:
        current_app.logger.error(f"Excel Parsing Error: {str(e)}")
    
    return quotes

def parse_pdf(file_path):
    # Placeholder for future PDF logic
    return [] 

def process_uploaded_file(file, user_id, is_admin):
    """Process uploaded file and save to DB"""
    saved_quotes = []
    errors = []
    
    try:
        # Save File
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Parse
        if file.filename.lower().endswith(('.xls', '.xlsx')):
            data = parse_excel(file_path)
        else:
            # Fallback/Placeholder for PDF
            data = parse_pdf(file_path)
        
        if not data:
            return [], ["No valid product data found. Please check your file columns."]

        # Save to Database
        for item in data:
            try:
                new_q = ProductQuote(
                    item_name=item['item_name'],
                    base_price=item['base_price'],
                    make_brand=item['make_brand'],
                    cas_no=item['cas_no'],
                    cat_no=item['cat_no'],
                    specifications=item['specifications'],
                    file_url=filename,  # CRITICAL: Saving filename for download
                    uploaded_by_id=user_id,
                    is_private=is_admin
                )
                db.session.add(new_q)
                saved_quotes.append(new_q)
            except Exception:
                continue
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        errors.append(f"Processing Error: {str(e)}")
        
    return saved_quotes, errors

def get_price_intelligence(query=None, user_is_admin=False):
    """Get aggregated price data for dashboard"""
    # Base Query
    q = ProductQuote.query
    if not user_is_admin: 
        q = q.filter_by(is_private=False)
    
    # Search Filter
    if query:
        term = f"%{query}%"
        q = q.filter(or_(
            ProductQuote.item_name.ilike(term), 
            ProductQuote.make_brand.ilike(term),
            ProductQuote.cas_no.ilike(term),
            ProductQuote.cat_no.ilike(term),
            ProductQuote.specifications.ilike(term)
        ))
    
    # Fetch all records
    all_quotes = q.all()
    
    # Grouping Logic
    data = {}
    for row in all_quotes:
        # Group by Item Name + Brand
        key = f"{row.item_name}|{row.make_brand}"
        
        if key not in data:
            data[key] = {
                'item_name': row.item_name, 
                'make_brand': row.make_brand, 
                'cas_no': row.cas_no, 
                'cat_no': row.cat_no,
                'specifications': row.specifications,
                'prices': [], 
                'count': 0, 
                'files': set() # Use set to avoid duplicate filenames
            }
        
        data[key]['prices'].append(row.base_price)
        data[key]['count'] += 1
        if row.file_url: 
            data[key]['files'].add(row.file_url)
        
    # Format Results
    results = []
    for k, v in data.items():
        # Pick the most recent file if multiple exist
        file_link = list(v['files'])[0] if v['files'] else None
        
        results.append({
            'item_name': v['item_name'],
            'make_brand': v['make_brand'],
            'cas_no': v['cas_no'], 
            'cat_no': v['cat_no'],
            'specifications': v['specifications'],
            'min_price': min(v['prices']),
            'max_price': max(v['prices']),
            'avg_price': sum(v['prices']) / len(v['prices']),
            'quote_count': v['count'],
            'file_url': file_link # This is what the UI needs for the button
        })
    
    # Sort alphabetically
    results.sort(key=lambda x: x['item_name'])
    return results

def get_motivational_quote():
    return "Innovation distinguishes between a leader and a follower."
