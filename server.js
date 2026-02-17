// Simple Express server to serve app and two API endpoints
import 'dotenv/config';
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import bodyParser from 'body-parser';
import pdfToPricelist from './api/pdf-to-pricelist.js';
import geminiPrice from './api/gemini-price.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(bodyParser.json({limit:'10mb'}));
app.use(express.static(__dirname));

app.post('/api/pdf-to-pricelist', pdfToPricelist);
app.post('/api/gemini-price', geminiPrice);

const port = process.env.PORT || 3000;
app.listen(port, ()=>{ 
  console.log('Server at http://localhost:'+port);
  if (process.env.GOOGLE_API_KEY) {
    console.log('✓ GOOGLE_API_KEY is configured');
  } else {
    console.log('✗ GOOGLE_API_KEY is NOT configured - Gemini API will not work');
    console.log('  Edit .env file and add your API key from: https://makersuite.google.com/app/apikey');
  }
});
