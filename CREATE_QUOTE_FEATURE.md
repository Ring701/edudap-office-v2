# Create Quote Feature - Documentation

## ✅ New Feature Added: Create Quote Page

A new "Create Quote" page has been added to the EduDAP Office v2 CRM system.

---

## 🎯 Features

### 1. Customer Details Section
- Reference Number (e.g., QTN/EDP/2025-26/0155)
- Date (Date picker)
- Customer Name
- Designation (e.g., Head, R & D)
- Organization Name
- Address

### 2. Product Search Section
- Search bar similar to Dashboard
- Search by Item Name, CAS No, Cat No, or Brand
- Real-time search results
- "Add" button for each product
- Products pulled from existing ProductQuote database

### 3. Quote Table
Columns:
- **S.No** - Serial number (auto)
- **Item Name** - Auto-filled from search
- **Unit** - Editable (default: "Unit")
- **Qty** - Editable (default: 1)
- **Make/Brand** - Auto-filled
- **Catalog No** - Auto-filled
- **Rate/Price** - Auto-filled from database
- **Discount** - Editable decimal (e.g., 0.1 for 10%)
- **Amount** - Auto-calculated: (Rate × Qty) - Discount
- **GST %** - Editable (default: 18%)
- **Total** - Auto-calculated: Amount + (Amount × GST%)

### 4. Automatic Calculations
- **Amount** = (Rate × Quantity) - (Rate × Quantity × Discount)
- **Total** = Amount + (Amount × GST%)
- Calculations update in real-time when Qty, Discount, or GST% changes

### 5. Print View
When "Print Quote" is clicked, opens a clean print-ready view with:
- Header: Ref. No. and Date
- Title: "QUOTATION" (centered, underlined)
- To Section: Customer details
- Salutation: "Respected Madam/Sir,"
- Intro Text: "We are glad to submit our quotation..."
- Table: All quote items with borders
- Grand Total: Sum of all item totals
- Print button for browser print dialog

---

## 📍 Access

- **URL**: `/quote/create`
- **Navigation**: "Create Quote" link in main navigation bar
- **Access**: Available to all logged-in users (admin and employees)

---

## 🎨 Design

- Uses existing color theme:
  - Deep Professional Blue (#004085) for headers
  - Scientific Green (#4E7D5B) for buttons
- Responsive Bootstrap 5 layout
- Professional print styling

---

## 🔧 Technical Details

### Files Added:
1. `app/quote.py` - Quote blueprint with routes
2. `app/templates/quote/create.html` - Quote creation form
3. `app/templates/quote/print.html` - Print-ready view

### Files Modified:
1. `app/__init__.py` - Registered quote blueprint
2. `app/templates/base.html` - Added "Create Quote" to navigation

### Routes:
- `GET /quote/create` - Show quote creation form
- `POST /quote/create` - Process form and redirect to print
- `GET /quote/search-products` - AJAX endpoint for product search
- `GET /quote/print` - Display print-ready quote

---

## 💡 Usage Instructions

1. **Navigate to Create Quote**
   - Click "Create Quote" in navigation bar

2. **Fill Customer Details**
   - Enter reference number, date, customer info

3. **Search and Add Products**
   - Type product name, CAS No, Cat No, or Brand in search bar
   - Click "Search" or press Enter
   - Click green "Add" button next to desired product
   - Product appears in quote table below

4. **Edit Quote Items**
   - Modify Unit, Qty, Discount, or GST% as needed
   - Amount and Total calculate automatically

5. **Remove Items**
   - Click red trash icon to remove an item

6. **Generate Quote**
   - Click "Print Quote" button
   - Print view opens in new page
   - Use browser print dialog (Ctrl+P) to print or save as PDF

---

## 🎯 Print View Features

- Clean, professional layout matching Excel format
- Print-optimized CSS (hides buttons when printing)
- Proper table borders and formatting
- Grand total calculation
- Browser print dialog integration

---

## 🔄 Integration

- Uses existing `ProductQuote` model for product data
- Respects visibility rules (admin sees private quotes, employees see public)
- Session-based storage for quote data
- No database changes required

---

## 📝 Notes

- Quote data is stored in session (temporary)
- For persistent storage, consider adding a Quote model in future
- Print view uses browser's native print functionality
- Can be saved as PDF using browser's "Save as PDF" option

---

**Status**: ✅ Complete and Ready  
**Added to ZIP**: ✅ Yes  
**Tested**: Ready for testing
