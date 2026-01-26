"""Utility functions for PDF/Excel parsing and price intelligence"""
import os
import re
from datetime import datetime
import pandas as pd
import PyPDF2
from flask import current_app
from app.models import ProductQuote, db

def parse_excel(file_path):
    """Parse Excel file with Smart Header Detection"""
    quotes = []
    try:
        # Step 1: Read the file WITHOUT headers first to scan it
        df_raw = pd.read_excel(file_path, header=None, engine='openpyxl')
        
        # Step 2: Hunt for the "Real" Header Row
        header_index = -1
        
        # Keywords to look for in the header row
        header_keywords = ['item', 'description', 'particulars', 'product', 'cat no', 'price', 'rate', 'amount']
        
        for idx, row in df_raw.iterrows():
            # Convert row to a single string to search for keywords
            row_text = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
            
            # If we find at least 2 keywords, this is likely the header row
            match_count = sum(1 for keyword in header_keywords if keyword in row_text)
            if match_count >= 2:
                header_index = idx
                break
        
        # Step 3: Reload dataframe using the correct header
        if header_index != -1:
            # Set the columns to the found header row
            df = df_raw.iloc[header_index + 1:].copy()
            df.columns = df_raw.iloc[header_index]
        else:
            # Fallback: Just assume the first row is the header if nothing found
            df = pd.read_excel(file_path, engine='openpyxl')

        # --- EXISTING MAPPING LOGIC (BUT IMPROVED) ---
        column_mapping = {
            'item_name': ['Item Name', 'Item', 'Product Name', 'Product', 'Name', 'Description', 'Particulars'],
            'cas_no': ['CAS No', 'CAS Number', 'CAS', 'CAS#'],
            'cat_no': ['Cat No', 'Catalog No', 'Cat Number', 'Product No', 'Cat#'],
            'make_brand': ['Make', 'Brand', 'Manufacturer', 'Company'],
            'base_price': ['Price', 'Base Price', 'Cost', 'Amount', 'Rate', 'Unit Price'],
            'gst_percent': ['GST', 'GST %', 'Tax', 'Tax %'],
            'specifications': ['Specifications', 'Specs', 'Details']
        }
        
        # Find actual column names
        actual_columns = {}
        for key, possible_names in column_mapping.items():
            for col in df.columns:
                if any(name.lower() in str(col).lower() for name in possible_names):
                    actual_columns[key] = col
                    break
        
        # Step 4: Extract Data (With "Footer Stopper")
        for idx, row in df.iterrows():
            try:
                # 1. Get the Item Name
                item_name = str(row.get(actual_columns.get('item_name', ''), '')).strip()
                
                # STOP if we hit the "Terms" or "Total" section (Footer detection)
                stop_words = ['total', 'terms', 'condition', 'amount in words', 'signature', 'sincerely']
                if any(word in item_name.lower() for word in stop_words):
                    break

                # SKIP invalid rows (empty or just numbers like "1", "2" from S.No column)
                if not item_name or item_name.lower() in ['nan', 'none', ''] or item_name.isdigit():
                    continue

                # 2. Extract Price safely
                raw_price = row.get(actual_columns.get('base_price', 0), 0)
                try:
                    # Remove currency symbols and commas if present
                    if isinstance(raw_price, str):
                        raw_price = re.sub(r'[^\d.]', '', raw_price)
                    base_price = float(raw_price)
                except:
                    base_price = 0.0

                # 3. Build the Quote Object
                quote_data = {
                    'item_name': item_name,
                    'cas_no': str(row.get(actual_columns.get('cas_no', ''), '')).strip() or None,
                    'cat_no': str(row.get(actual_columns.get('cat_no', ''), '')).strip() or None,
                    'make_brand': str(row.get(actual_columns.get('make_brand', ''), 'Unknown')).strip(),
                    'base_price': base_price,
                    'gst_percent': float(row.get(actual_columns.get('gst_percent', 18), 18)) or 18.0,
                    'specifications': str(row.get(actual_columns.get('specifications', ''), '')).strip() or None
                }
                
                # Only add if price is valid
                if quote_data['base_price'] > 0:
                    quotes.append(quote_data)

            except Exception as e:
                # Log error but keep going for other rows
                current_app.logger.warning(f"Skipping row {idx}: {str(e)}")
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
            
            lines = text.split('\n')
            current_quote = {}
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Extract CAS Number
                cas_match = re.search(r'CAS[:\s-]*(\d{2,7}-\d{2}-\d)', line, re.IGNORECASE)
                if cas_match: current_quote['cas_no'] = cas_match.group(1)
                
                # Extract Catalog Number
                cat_match = re.search(r'(?:Cat|Catalog|Product)[\s#:]*([A-Z0-9\-]+)', line, re.IGNORECASE)
                if cat_match: current_quote['cat_no'] = cat_match.group(1)
                
                # Extract Price
                price_match = re.search(r'[₹$€£]?\s*(\d+[.,]\d{2})', line)
                if price_match:
                    try:
                        price_str = price_match.group(1).replace(',', '.')
                        current_quote['base_price'] = float(price_str)
                    except: pass
                
                # Extract Brand
                brand_match = re.search(r'(?:Make|Brand|Manufacturer)[:\s]+([A-Z][A-Za-z0-9\s]+)', line, re.IGNORECASE)
                if brand_match: current_quote['make_brand'] = brand_match.group(1).strip()
            
            # If we found data, create a generic item entry
            if current_quote and 'base_price' in current_quote:
                item_name = lines[0] if lines else "Unknown Item"
                current_quote['item_name'] = item_name[:200]
                current_quote['make_brand'] = current_quote.get('make_brand', 'Unknown')
                current_quote['gst_percent'] = 18.0
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
        
        # Ensure directory exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'quotes')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
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
        
        if not quotes_data:
            errors.append("No valid product data found in file. Please check table headers.")
            return saved_quotes, errors

        # Process each quote
        for quote_data in quotes_data:
            try:
                # Deduplication: Check if quote exists
                existing = ProductQuote.query.filter_by(
                    item_name=quote_data['item_name'],
                    make_brand=quote_data['make_brand'],
                    base_price=quote_data['base_price']
                ).first()
                
                if existing:
                    existing.specifications = quote_data.get('specifications') or existing.specifications
                    existing.file_url = file_path
                    existing.created_at = datetime.utcnow()
                    saved_quotes.append(existing)
                else:
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
                        is_private=is_admin
                    )
                    db.session.add(new_quote)
                    saved_quotes.append(new_quote)
                    
            except Exception as e:
                current_app.logger.error(f"Error saving quote: {str(e)}")
        
        db.session.commit()
        
    except Exception as e:
        errors.append(f"Error processing file: {str(e)}")
        current_app.logger.error(f"Error processing uploaded file: {str(e)}")
        db.session.rollback()
    
    return saved_quotes, errors

def get_price_intelligence(query=None, user_is_admin=False):
    """Get price intelligence with min/max grouping by brand"""
    if user_is_admin:
