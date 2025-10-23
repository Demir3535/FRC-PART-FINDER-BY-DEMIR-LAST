# AI Integration Plan for FRC Parts Finder

## Current Limitations
- Manual product data entry
- Limited to pre-defined parts
- No real-time price updates
- No automatic stock checking

## AI Integration Options

### Option 1: Web Scraping with AI (Recommended for FRC)
Use AI to intelligently scrape FRC vendor websites:

**Benefits:**
- Real-time prices
- Actual stock status
- Automatic updates
- Handles multiple vendors

**Implementation:**
1. **Backend Service** (Node.js + Puppeteer/Cheerio)
   ```javascript
   // Example: Scrape AndyMark
   async function scrapeAndyMark(query) {
       const response = await fetch(`https://www.andymark.com/search?q=${query}`);
       const html = await response.text();
       // Parse HTML for products, prices, stock
       return products;
   }
   ```

2. **AI-Powered Parser** (OpenAI GPT or Claude)
   - Send HTML to AI
   - AI extracts product info
   - Returns structured JSON

   ```javascript
   const aiPrompt = `
   Extract product information from this HTML:
   - Product name
   - Price
   - Stock status
   - Product URL

   HTML: ${html}
   `;
   ```

### Option 2: Google Custom Search API
Use Google to find products across vendors:

**Setup:**
```javascript
const GOOGLE_API_KEY = 'your_key';
const SEARCH_ENGINE_ID = 'your_cx';

async function searchWithGoogle(query) {
    const url = `https://www.googleapis.com/customsearch/v1?key=${GOOGLE_API_KEY}&cx=${SEARCH_ENGINE_ID}&q=${query} FRC`;
    const response = await fetch(url);
    return await response.json();
}
```

### Option 3: OpenAI Function Calling (Most Intelligent)
Let AI decide which vendor to search and how:

```javascript
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function searchWithAI(userQuery) {
    const completion = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
            {
                role: "system",
                content: "You are an FRC parts expert. Search for parts across REV, AndyMark, VEX, and WCP."
            },
            {
                role: "user",
                content: `Find: ${userQuery}`
            }
        ],
        functions: [
            {
                name: "search_vendor",
                description: "Search a specific FRC vendor",
                parameters: {
                    type: "object",
                    properties: {
                        vendor: { type: "string", enum: ["REV", "AndyMark", "VEX", "WCP"] },
                        query: { type: "string" }
                    }
                }
            }
        ]
    });

    // AI will call the function with optimal parameters
    return completion.choices[0].message;
}
```

## Recommended Implementation Plan

### Phase 1: Basic Backend (This Weekend)
1. Create Node.js/Express backend
2. Add web scraping for one vendor (AndyMark)
3. Test with NEO Motor, Falcon 500

### Phase 2: Multi-Vendor Support (Next Week)
1. Add REV Robotics scraper
2. Add VEX Robotics scraper
3. Add WCP scraper
4. Consolidate results

### Phase 3: AI Integration (Week 2)
1. Add OpenAI/Claude API
2. Use AI to parse messy HTML
3. Use AI to match user queries intelligently
4. Add caching for common searches

### Phase 4: Real-time Updates (Week 3)
1. Add background job to refresh prices
2. Store data in database (MongoDB/PostgreSQL)
3. Add "Last Updated" timestamps
4. Show price history graphs

## File Structure for Backend

```
frc-parts-finder/
├── frontend/          (current files)
│   ├── index.html
│   ├── css/
│   └── js/
├── backend/
│   ├── server.js
│   ├── scrapers/
│   │   ├── andymark.js
│   │   ├── rev.js
│   │   ├── vex.js
│   │   └── wcp.js
│   ├── ai/
│   │   └── openai.js
│   └── routes/
│       └── search.js
└── package.json
```

## Quick Start: Simple Backend

```javascript
// backend/server.js
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/search', async (req, res) => {
    const { query } = req.query;

    // Scrape vendors
    const results = await Promise.all([
        scrapeAndyMark(query),
        scrapeREV(query),
        scrapeVEX(query),
        scrapeWCP(query)
    ]);

    // Flatten results
    const allResults = results.flat();

    res.json(allResults);
});

app.listen(3000, () => {
    console.log('Backend running on http://localhost:3000');
});
```

## Frontend Changes Needed

```javascript
// Update searchParts() function
async function searchParts() {
    const searchQuery = document.getElementById('searchInput').value.trim();

    // Call backend instead of mock data
    const response = await fetch(`http://localhost:3000/api/search?query=${encodeURIComponent(searchQuery)}`);
    const results = await response.json();

    displayResults(results);
}
```

## Cost Estimates

### Option 1: Web Scraping Only
- **Cost:** $0-5/month (server hosting)
- **Complexity:** Medium
- **Accuracy:** High

### Option 2: Google API
- **Cost:** $5/1000 queries
- **Complexity:** Low
- **Accuracy:** Medium

### Option 3: OpenAI GPT-4
- **Cost:** $0.03/1K tokens (~$1-2/day)
- **Complexity:** Medium
- **Accuracy:** Very High

## Next Steps

1. **Choose Option:** I recommend Option 1 (Web Scraping) + Option 3 (AI parsing)
2. **Set up backend:** Node.js + Express
3. **Add one scraper:** Test with AndyMark
4. **Deploy:** Vercel (frontend) + Railway/Render (backend)

Ready to start? I can help build the backend! 🚀
