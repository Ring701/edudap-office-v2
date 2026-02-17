# EduDAP Quotation System

A intelligent quotation generation system with A/B/C pricing tiers, powered by Gemini AI for web-based price estimation.

## 🚀 Features

- **Knowledge Base Indexing**: Index your Price Lists and Past Quotations from Excel files
- **A/B/C Pricing Tiers**:
  - **Tier A**: Past quotations (customer-specific historical pricing)
  - **Tier B**: Price list (MRP with customer-type-based discounts)
  - **Tier C**: Gemini web search (grounded AI pricing with citations)
- **Smart Quotation Generation**: Automatic fallback through pricing tiers
- **Print-Ready Output**: Professional quotation format with PDF export
- **Citation Tracking**: Source URLs for web-sourced prices

## 📋 Requirements

- Node.js 18+ 
- Chrome or Edge browser (for folder access)
- Google Gemini API key

## 🔧 Setup Instructions

### 1. Clone or Download the Project

```bash
git clone https://github.com/Ring701/edudap-office-v2.git
cd edudap-office-v2
```

### 2. Install Dependencies

This project uses ES modules and requires Node.js 18+.

```bash
npm install
```

### 3. Set Up Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
PORT=3000
```

**Get your Gemini API key**: https://makersuite.google.com/app/apikey

### 4. Run Locally

```bash
npm run dev
```

The server will start at `http://localhost:3000`

Open your browser and navigate to:
- **Quotation System**: http://localhost:3000/index.html

## 📖 How to Use

### Step 1: Select Knowledge Base Folder

1. Click "📁 Select Folder"
2. Choose a folder containing your Excel files (Price Lists and Past Quotations)
3. The system will index all `.xlsx` and `.xls` files

**Supported Excel Formats:**

**Price Lists** (detected by filename containing "price/rate/pricelist" or columns "price/mrp"):
```
Item | Price | Discount | MRP
```

**Past Quotations** (detected by filename containing "quote/quotation" or column "customer"):
```
Customer | Item | Price | Discount
```

### Step 2: Configure Gemini (Optional)

- **Serverless Endpoint**: Default is `/api/gemini-price` (already configured)
- **API Key**: Can be set in `.env` or entered in the UI
- **Suggested URLs**: Comma-separated URLs to prioritize in Gemini's search

### Step 3: Fill Quotation Header

- **Quotation No**: e.g., `QTN/EDP/2025-26/0155`
- **Date**: Auto-filled with today's date
- **To (Recipient)**: Customer name
- **University/Organization**: Customer organization
- **Customer Type**: University/Company/Govt/PSU (affects discount rates)

### Step 4: Upload Requirements Excel

Upload an Excel file with the following columns (case-insensitive):

| Column | Description |
|--------|-------------|
| Customer | Customer name (optional, matches with history) |
| Item | Product/item name (required) |
| Quantity | Order quantity (defaults to 1) |
| Specification | Item specs (optional) |
| Unit | Unit of measure (optional) |
| Make | Brand/manufacturer (optional) |
| Cat no | Catalog number (optional) |

**Example Requirements Excel:**
```
Customer | Item | Quantity | Specification | Unit | Make | Cat no
IIT Bombay | Pipette 10ml | 50 | Class A | pcs | Eppendorf | 12345
Tropical Genetics | PCR Tubes | 1000 | 0.2ml | pcs | Corning | 67890
```

### Step 5: Generate Quotation

1. Click "⚡ Generate"
2. The system will:
   - Check past quotations for each item (Tier A)
   - Fall back to price list (Tier B)
   - Finally use Gemini web search (Tier C)
3. Review the generated quotation
4. Click "🖨️ Print / Save PDF" to export

## 🌐 Deploy to Vercel

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variable in Vercel dashboard
# Settings > Environment Variables
# GOOGLE_API_KEY = your_api_key
```

### Option 2: Vercel Dashboard

1. Push your code to GitHub
2. Go to https://vercel.com/new
3. Import your repository
4. Vercel will detect the project automatically
5. Add `GOOGLE_API_KEY` in Environment Variables
6. Click "Deploy"

**Important**: After deployment, your quotation system will be available at:
```
https://your-project-name.vercel.app/index.html
```

## 📁 Project Structure

```
edudap-office-v2/
├── index.html          # Frontend quotation interface
├── index.js            # Express server with Gemini API
├── package.json        # Dependencies and scripts
├── vercel.json         # Vercel deployment config
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔍 Pricing Logic

### Tier A: Past Quotations
- Searches indexed past quotations for customer + item match
- Uses historical pricing with original discount
- Best for repeat customers

### Tier B: Price List
- Searches price list for item match
- Applies customer-type-based discounts:
  - University: 10% default
  - Company: 5% default
  - Govt/PSU: 5% default

### Tier C: Gemini Web Search
- Uses Gemini 2.5 Flash with Google Search Grounding
- Searches Indian vendors, marketplaces, distributors
- Provides current market pricing with automatic citation extraction
- Considers customer type for rate suggestions
- Returns grounded URLs from search results

## 🐛 Troubleshooting

### "Folder access requires Chrome/Edge and HTTPS or localhost"
- Use Chrome or Edge browser
- Access via `http://localhost:3000` (not `file://`)
- For production, use HTTPS

### "Google API key is required"
- Set `GOOGLE_API_KEY` in `.env` file
- Or enter API key in the UI (Step 2)
- Get API key from: https://makersuite.google.com/app/apikey

### Gemini API fails
- Check your API key is valid
- Ensure you have available quota
- Try with suggested URLs for better results

### Prices seem incorrect
- Update your knowledge base with accurate data
- Add relevant suggested URLs for Gemini
- Verify customer type is set correctly

## 📝 License

This project is proprietary and confidential to EduDAP.

## 👤 Contact

**Praveen Tiwari**  
Director, EduDAP  
Email: Praveen@edudap.com  
Phone: 9818315018