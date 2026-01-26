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
    """Parse Excel file with Stricter Rules"""
    quotes = []
    try:
        # Read file
        df_raw = pd.read_excel(file_path, header=None, engine='openpyxl', dtype=str)
        
        # 1. Find the Header Row
        header_index = -1
        header_keywords = ['item', 'description', 'particulars', 'product', 'cat no', 'price', 'rate', 'amount']
        
        for idx, row in df_raw.iterrows():
            row_text = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
            if sum(1 for k in header_keywords if k in row_text) >= 2:
                header_index = idx
                break
        
        if header_index != -1:
            df = df_raw.iloc[header_index + 1:].copy()
            df.columns = df_raw.iloc[header_index]
        else:
            df = pd.read_excel(file_path, engine='openpyxl')

        # 2. Strict Column Mapping
        # We explicitly separate "Item Name" from "Serial Number"
        actual_columns = {}
        
        # Helper to find column
        def find_col(keywords, anti_keywords=[]):
            for col in df.columns:
                col_str = str(col).lower()
                # Must contain a keyword
                if any(k in col_str for k in keywords):
                    # Must NOT contain anti-keywords (Like "No." or "Sr.")
                    if not any(ak in col_str for ak in anti_keywords):
                        return col
            return None

        # Map 'item_name' but avoid 'S.No'
        actual_columns['item_name'] = find_col(
            ['item', 'description', 'product', 'particulars', 'name'], 
            anti_keywords=['no.', 'sr.', 'serial', 'code', 'qty']
        )
        
        # Map Price
        actual_columns['base_price'] = find_col(['price', 'rate', 'amount', 'cost'])
        
        # Map Others
        actual_columns['cas_no'] = find_col(['cas'])
        actual_columns['cat_no'] = find_col(['cat', 'catalog'])
        actual_columns['make_brand'] = find_col(['make', 'brand'])
        actual_columns['specifications'] = find_col(['spec', 'pack'])

        # If we couldn't find an Item Name column, abort (don't guess)
        if not actual_columns['item_name']:
            current_app.logger.warning("Could not find a valid Item Name column. Aborting.")
            return []

        # 3. Extract Data
        for idx, row in df.iterrows():
            try:
                # Extract Item Name
                item_name = str(row.get(actual_columns['item_name'], '')).strip()
                
                # Footer detection
                if any(x in item_name.lower() for x in ['total', 'terms', 'signature', 'amount in words']):
                    break

                # --- NUCLEAR FILTER: IGNORE JUNK ---
                # If it's a number (like "1" or "10"), IGNORE IT.
                if not item_name or item_name.replace('.','').isdigit() or len(item_name) < 3:
                    continue
                # If it looks like "1.", "2.", IGNORE IT.
                if re.match(r'^\d+\.?$', item_name):
                    continue

                # Extract Price
                base_price = 0.0
                if actual_columns['base_price']:
                    raw_price = str(row.get(actual_columns['base_price'], 0))
                    clean_price = re.sub(r'[^\d.]', '', raw_price)
                    try:
                        base_price = float(clean_price)
                    except: pass

                if base_price > 0:
                    quotes.append({
                        'item_name': item_name,
                        'cas_no': str(row.get(actual_columns.get('cas_no'), '')).strip() if actual_columns.get('cas_no') else None,
                        'cat_no': str(row.get(actual_columns.get('cat_no'), '')).strip() if actual_columns.get('cat_no') else None,
                        'make_brand': str(row.get(actual_columns.get('make_brand'), 'Unknown')).strip() if actual_columns.get('make_brand') else 'Unknown',
                        'base_price': base_price,
                        'gst_percent': 18.0,
                        'specifications': str(row.get(actual_columns.get('specifications'), '')).strip() if actual_columns.get('specifications') else None
                    })
            except: continue
            
    except Exception as e:
        current_app.logger.error(f"Error parsing Excel: {e}")
    
    return quotes

def parse_pdf(file_path):
    return [] # Keeping simple for now

def process_uploaded_file(file, user_id, is_admin):
    saved = []
    errs = []
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file.save(path)
        
        data = parse_excel(path) if file.filename.endswith(('.xls','.xlsx')) else []
        
        if not data:
            return [], ["No valid data found. Check your file format."]

        for item in data:
            try:
                new_q = ProductQuote(
                    item_name=item['item_name'],
                    cas_no=item['cas_no'],
                    cat_no=item['cat_no'],
                    make_brand=item['make_brand'],
                    base_price=item['base_price'],
                    gst_percent=18.0,
                    specifications=item['specifications'],
                    file_url=filename, # JUST STORE FILENAME FOR URL
                    uploaded_by_id=user_id,
                    is_private=is_admin
                )
                db.session.add(new_q)
                saved.append(new_q)
            except: continue
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        errs.append(str(e))
        
    return saved, errs

def get_price_intelligence(query=None, user_is_admin=False):
    q = ProductQuote.query
    if not user_is_admin: q = q.filter_by(is_private=False)
    
    if query:
        term = f"%{query}%"
        q = q.filter(or_(ProductQuote.item_name.ilike(term), ProductQuote.cas_no.ilike(term)))
    
    data = {}
    for row in q.all():
        key = f"{row.item_name}|{row.make_brand}"
        if key not in data:
            data[key] = {
                'item_name': row.item_name, 'make_brand': row.make_brand, 
                'prices': [], 'count': 0, 'files': set()
            }
        data[key]['prices'].append(row.base_price)
        data[key]['count'] += 1
        if row.file_url:
            data[key]['files'].add(row.file_url)
        
    res = []
    for k, v in data.items():
        # Get the most recent file if multiple
        file_link = list(v['files'])[0] if v['files'] else None
        res.append({
            'item_name': v['item_name'],
            'make_brand': v['make_brand'],
            'min_price': min(v['prices']),
            'max_price': max(v['prices']),
            'avg_price': sum(v['prices'])/len(v['prices']),
            'quote_count': v['count'],
            'cas_no': 'N/A', 'cat_no': 'N/A', 'specifications': 'N/A',
            'file_url': file_link # SEND FILE LINK TO FRONTEND
        })
    return res

def get_motivational_quote():
    return "Keep pushing forward."
