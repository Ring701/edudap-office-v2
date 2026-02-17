// /api/pdf-to-pricelist.js
// Naive PDF text structurer: best-effort extraction of item, unit, price
export default async function handler(req, res){
  try{
    const { text, fileName, bytesBase64 } = req.body||{};
    if ((!text || text.trim().length<50) && !bytesBase64){
      return res.status(400).json({ error:'No text/bytes provided' });
    }
    const src = (text||'');
    const lines = src.split(/\n|\r/).map(s=>s.trim()).filter(Boolean);

    // Heuristic: group tokens with a unit and a price number on same/nearby lines
    const items=[];
    for (let i=0;i<lines.length;i++){
      const L = lines[i];
      // unit
      const unitMatch = L.match(/\b(\d{1,3}(?:\.\d+)?)(?:\s?)(gm|g|kg|ml|ltr|l)\b/i);
      // price (integer/decimal)
      const priceMatch = L.match(/\b(\d{2,6}(?:\.\d{1,2})?)\b/);
      if (!unitMatch || !priceMatch) continue;
      // item name likely on this or previous line
      const cand = [lines[i-1]||'', L, lines[i+1]||''].join(' ');
      // prune noisy tokens
      let item = cand.replace(/\b(HSN|GST|CAS|CAT|CODE|Product|Price|Rate|UNIT|ITEM)\b.*$/i,'').trim();
      // Keep a reasonable slice
      item = item.split(/\s{2,}/)[0];
      const unitVal = unitMatch[1] + ' ' + unitMatch[2];
      const price = Number(priceMatch[1]);
      if (!isFinite(price)) continue;
      // Avoid duplicates by item+unit+price
      const key = item.toLowerCase()+unitVal.toLowerCase()+price;
      if (items.some(x=>x.__k===key)) continue;
      items.push({ item, unit:unitVal, mrp:price, __k:key });
      if (items.length>1000) break;
    }

    // Add vendor hint from filename
    const make = (fileName||'').toLowerCase().includes('cdh')? 'CDH' : (fileName||'').toLowerCase().includes('bb')? 'BBChem' : '';
    items.forEach(r=>{ if (make && !r.make) r.make = make; });

    return res.status(200).json(items.map(({__k, ...rest})=>rest));
  }catch(e){
    return res.status(500).json({ error:String(e?.message||e) });
  }
}