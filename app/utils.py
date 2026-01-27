"""Utility functions"""
import os
import re
import pandas as pd
from flask import current_app
from app.models import ProductQuote, db
from sqlalchemy import or_
from datetime import datetime

def parse_excel(file_path):
    quotes = []
    try:
        # Read without headers first to find the real start
        df_raw = pd.read_excel(file_path, header=None, engine='openpyxl', dtype=str)
        
        header_index = -1
        keywords = ['item', 'description', 'product', 'particulars']
        
        for idx, row in df_raw.head(20).iterrows():
            text = ' '.join([str(v).lower() for v in row.values if pd.notna(v)])
            if any(k in text for k in keywords):
                header_index = idx
                break
        
        if header_index != -1:
            df = df_raw.iloc[header_index + 1:].copy()
            df.columns = df_raw.iloc[header_index]
        else:
            df = pd.read_excel(file_path, engine='openpyxl')

        # Find columns
        def get_col(candidates):
            for col in df.columns:
                if any(c in str(col).lower() for c in candidates):
                    return col
            return None

        col_item = get_col(['item', 'description', 'product', 'particulars'])
        col_price = get_col(['price', 'rate', 'amount'])
        col_make = get_col(['make', 'brand'])
        
        if not col_item: return []

        for idx, row in df.iterrows():
            try:
                item_name = str(row.get(col_item, '')).strip()
                
                # --- STRICT FILTER ---
                if not item_name or item_name.lower() in ['nan', 'none']: continue
                if item_name.replace('.', '').isdigit(): continue  # Skips "1", "10", "11"
                if len(item_name) < 2: continue
                if 'total' in item_name.lower(): break
                
                raw_price = str(row.get(col_price, 0)) if col_price else '0'
                clean_price = re.sub(r'[^\d.]', '', raw_price)
                try: price = float(clean_price)
                except: price = 0.0

                if price > 0:
                    quotes.append({
                        'item_name': item_name,
                        'base_price': price,
                        'make_brand': str(row.get(col_make, 'Unknown')).strip() if col_make else 'Unknown',
                        'specifications': None, 'cas_no': None, 'cat_no': None
                    })
            except: continue
    except Exception as e:
        current_app.logger.error(f"Error: {e}")
    return quotes

def parse_pdf(file_path): return []

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
        
        if not data: return [], ["No valid data found."]

        for item in data:
            new_q = ProductQuote(
                item_name=item['item_name'],
                base_price=item['base_price'],
                make_brand=item['make_brand'],
                file_url=filename, # Saves filename
                uploaded_by_id=user_id,
                is_private=is_admin
            )
            db.session.add(new_q)
            saved.append(new_q)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        errs.append(str(e))
    return saved, errs

def get_price_intelligence(query=None, user_is_admin=False):
    q = ProductQuote.query
    if not user_is_admin: q = q.filter_by(is_private=False)
    if query:
        q = q.filter(or_(ProductQuote.item_name.ilike(f"%{query}%"), ProductQuote.make_brand.ilike(f"%{query}%")))
    
    data = {}
    for row in q.all():
        key = f"{row.item_name}|{row.make_brand}"
        if key not in data:
            data[key] = {'item_name': row.item_name, 'make_brand': row.make_brand, 'prices': [], 'files': []}
        data[key]['prices'].append(row.base_price)
        if row.file_url: data[key]['files'].append(row.file_url)
        
    res = []
    for k, v in data.items():
        res.append({
            'item_name': v['item_name'],
            'make_brand': v['make_brand'],
            'min_price': min(v['prices']),
            'max_price': max(v['prices']),
            'avg_price': sum(v['prices'])/len(v['prices']),
            'quote_count': len(v['prices']),
            'file_url': v['files'][0] if v['files'] else None # Sends file to template
        })
    return res

def get_motivational_quote():
    return "Great things never come from comfort zones."
