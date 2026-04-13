# OSINT Phone Correlator

Tool for automating phone number OSINT investigations and preparing structured data for correlation analysis.

## Features

- Search phone numbers across multiple platforms
- Support for multiple phone formats (+34, 0034, spaced variants)
- Custom search queries (escort-related, domain-specific)
- Uses `ddgs` for more reliable search results
- JSON result export
- Deduplication of results
- Detection of ad type:
  - `individual`
  - `group`
  - `duo`
- Confidence classification system:
  - `high` → confirmed phone match with strong signals
  - `medium` → partial match or contextual relevance
  - `low` → likely noise or generic listings
- Designed for correlation and pattern detection workflows

## Usage

```bash
python search_phone.py --phone 660XXXXXXX
```

## Example Output
```json
[
    {
        "query": "\"660XXXXXX\"",
        "title": "Example listing",
        "link": "https://example.com/ad.html",
        "domain": "example.com",
        "type": "individual",
        "score": 4,
        "phone_match": true,
        "confidence": "high"
    }
]
```

## How It Works
### 1. Generates multiple variants of the phone number:

- Raw number
- +34 format
- 0034 format
- Spaced format

### 2. Builds search queries:
- Generic queries
- Escort-related queries
- Domain-specific queries

### 3. Retrieves results using DuckDuckGo (ddgs)

### 4. Applies filtering:
- Keeps only relevant domains
- Removes generic/category pages
- Keeps links that resemble real ad pages

### 5. Processes each result:
- Detects ad type (individual / group / duo)
- Checks if phone appears in title/link
- Assigns a score based on relevance

### 6. Classifies confidence:
- High → strong match + good structure
- Medium → partial relevance
- Low → weak or noisy result

### 7. Outputs structured JSON ready for analysis

---

## Current Limitations
- Results depend on search engine behavior
- Some platforms introduce SEO-heavy noise
- Phone detection is based on title/link only (no full page parsing)
- No automatic correlation or clustering yet

## Roadmap
- Correlation engine (group results by phone number)
- Detection of reused phone numbers across profiles
- Pattern detection (agency / multi-profile behavior)
- Export to CSV / Excel
- Optional full-page scraping for deeper validation

## Notes
This project is part of a broader OSINT workflow focused on data correlation rather than simple data collection.

The objective is to transform raw search results into structured and actionable intelligence.
