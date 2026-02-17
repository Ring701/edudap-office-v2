// /api/gemini-price.js
// Serverless-style handler. If GOOGLE_API_KEY is set, uses Gemini with Google Search grounding.
import { GoogleGenerativeAI } from '@google/generative-ai';

export default async function handler(req, res){
  try{
    const { item, spec, qty, customerType, suggestedUrls=[], apiKey } = req.body||{};
    const key = process.env.GOOGLE_API_KEY || apiKey;
    if (!key){ return res.status(501).json({ error:'Set GOOGLE_API_KEY on server or pass apiKey in body.' }); }

    const genai = new GoogleGenerativeAI(key);
    // Use Flash for speed; Search grounding enabled via tool
    const model = genai.getGenerativeModel({ model: 'gemini-2.0-flash-exp', tools: [{ googleSearchRetrieval: {} }] });

    const prompt = `You are pricing lab chemicals for an Indian academic quotation. Return one JSON only with fields: {unit:number, currency:'INR', citations:[{title, url}]}.
Item: ${item}
Specs (if any): ${spec||''}
Qty: ${qty||1}
Customer Type: ${customerType||''}
${suggestedUrls?.length? `Preferred sources: ${suggestedUrls.join(', ')}` : ''}
Rules: unit is the per-pack MRP in INR for the most common vendor pack (use 500 gm or 2.5 L where relevant). Include 1-3 citations. No prose.`;

    const result = await model.generateContent({ contents:[{ role:'user', parts:[{ text: prompt }]}] });
    const text = result.response.text();
    // attempt to extract JSON
    const json = JSON.parse(text.match(/\{[\s\S]*\}/)?.[0]||'{}');
    return res.status(200).json({ source:'C', ...json });
  }catch(e){ return res.status(500).json({ error:String(e?.message||e) }); }
}