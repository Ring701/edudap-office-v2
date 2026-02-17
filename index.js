import express from 'express';
import cors from 'cors';
import { GoogleGenAI } from '@google/genai';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files (the index.html)
app.use(express.static('.'));

// Gemini Price Estimation Endpoint
app.post('/api/gemini-price', async (req, res) => {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'POST only' });
    }

    const {
      item, spec, qty = 1, customerType = 'Company',
      suggestedUrls = [], apiKey
    } = req.body || {};

    if (!item) {
      return res.status(400).json({ error: 'Missing item' });
    }

    // Get API key from request body or environment variable
    const GOOGLE_API_KEY = apiKey || process.env.GOOGLE_API_KEY;

    if (!GOOGLE_API_KEY) {
      return res.status(400).json({ 
        error: 'Google API key is required. Provide it via API key field or set GOOGLE_API_KEY environment variable.' 
      });
    }

    // Initialize Gemini with Google Search Grounding
    const ai = new GoogleGenAI({ apiKey: GOOGLE_API_KEY });
    
    // Enable Google Search Grounding
    const tools = [{ google_search: {} }];

    const suggestText = suggestedUrls.length
      ? `Prefer information from these URLs if relevant and current:\n${suggestedUrls.join('\n')}\n`
      : '';

    const promptParts = [
      { text: `Estimate current India market unit price in INR for "${item}".` },
      { text: `Specs: ${spec || 'N/A'}. Quantity: ${qty}. Customer type: ${customerType}.` },
      { text: `Choose a widely-available mid configuration sold in India.` },
      { text: `Return ONLY compact JSON: {"unit": <integer>, "currency":"INR"}.` },
      { text: suggestText }
    ].map(p => ({ text: p.text }));

    const resp = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [{ role:'user', parts: promptParts }],
      config: {
        tools,
        response_modalities: ['TEXT']
      }
    });

    // Get text from response - check different possible response structures
    let txt = '';
    if (typeof resp.text === 'function') {
      txt = resp.text() || '{}';
    } else if (resp.response?.text) {
      txt = resp.response.text();
    } else if (resp.candidates?.[0]?.content?.parts?.[0]?.text) {
      txt = resp.candidates[0].content.parts[0].text;
    } else {
      txt = '{}';
    }

    const m = txt.match(/\{[\s\S]*\}/);
    let unit = 0;
    try { 
      unit = Math.round(JSON.parse(m ? m[0] : '{}').unit || 0); 
    } catch (e) {
      console.error('Failed to parse unit price:', e);
    }

    // Citations from grounding metadata (if present)
    const cand = resp.candidates?.[0];
    const cites = cand?.grounding_metadata?.web?.results?.map(r=>r?.uri).filter(Boolean) || [];

    res.status(200).json({
      source:'C',
      unit,
      total: unit * (qty||1),
      currency:'INR',
      citations: cites
    });

  } catch (error) {
    console.error('Gemini API Error:', error);
    res.status(500).json({ 
      error: 'Failed to get price estimate from Gemini',
      details: error.message
    });
  }
});

// PDF-to-Price List endpoint (structures PDF text into price list items)
app.post('/api/pdf-to-pricelist', async (req, res) => {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'POST only' });
    }

    const { text, apiKey } = req.body || {};

    if (!text || text.length < 20) {
      return res.status(400).json({ error: 'No PDF text provided' });
    }

    // Get API key from request body or environment variable
    const GOOGLE_API_KEY = apiKey || process.env.GOOGLE_API_KEY;

    if (!GOOGLE_API_KEY) {
      return res.status(400).json({ 
        error: 'Google API key is required. Provide it via API key field or set GOOGLE_API_KEY environment variable.' 
      });
    }

    // Initialize Gemini
    const ai = new GoogleGenAI({ apiKey: GOOGLE_API_KEY });

    // Ask Gemini to structure raw PDF text to a clean price list
    const promptParts = [
      { text: "You will receive raw text extracted from a product price list PDF (India)." },
      { text: "Extract a structured list of items with fields: item, mrp, discount (if present), unit (e.g., '500 gm', '2.5 L'), catno (CAT NO / Product Code), grade (AR/EP/HPLC/MB), and if possible a 'make' inferred from the document (publisher/vendor brand)." },
      { text: "Output ONLY compact JSON array like: [{\"item\":\"...\",\"mrp\":12345,\"discount\":10,\"unit\":\"500 gm\",\"catno\":\"ABC-123\",\"grade\":\"AR\",\"make\":\"CDH\"}, ...]." },
      { text: "Assume currency is INR and 'rate'/'price'/'mrp' are per-unit list prices." },
      { text: "Ignore headers, page numbers, and non-product lines." },
      { text: `Text:\n${text.slice(0, 160000)}` } // keep prompt reasonable
    ].map(p => ({ text: p.text }));

    const resp = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [{ role:'user', parts: promptParts }],
      config: { response_modalities: ['TEXT'] }
    });

    const raw = resp.text() || '[]';
    const m = raw.match(/\[[\s\S]*\]/);
    const arr = JSON.parse(m ? m[0] : '[]');

    res.status(200).json(arr);

  } catch (error) {
    console.error('PDF-to-pricelist Error:', error);
    res.status(500).json({ 
      error: 'Failed to structure PDF text into price list',
      details: error.message
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   EduDAP Quotation System - Server Running                ║
║                                                           ║
║   📂 Server: http://localhost:${PORT}                      ║
║   📄 Quotation: http://localhost:${PORT}/index.html        ║
║                                                           ║
║   📋 Features:                                            ║
║   ✅ Knowledge Base Indexing                              ║
║   ✅ A/B/C Pricing Tiers                                  ║
║   ✅ Gemini Web Price Fallback                            ║
║   ✅ Print/Export to PDF                                  ║
║                                                           ║
║   🔑 Set GOOGLE_API_KEY environment variable             ║
║      or provide API key in the UI                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});