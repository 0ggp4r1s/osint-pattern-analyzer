# OSINT Pattern Analyzer

Tool for automating OSINT investigations across multiple identity vectors (phone numbers, usernames and future email support), designed to extract structured data and enable pattern detection and correlation analysis.

## Features

### Phone OSINT
- Search phone numbers across multiple platforms
- Support for multiple phone formats (+34, 0034, spaced variants)
- Custom search queries (escort-related, domain-specific)
- Detection of ad type:
  - `individual`
  - `group`
  - `duo`
- Phone presence validation (`phone_match`)
- Confidence classification system:
  - `high` → confirmed phone match with strong signals
  - `medium` → partial match or contextual relevance
  - `low` → likely noise or generic listings

### Username OSINT
- Search usernames across multiple platforms:
  - social media
  - messaging platforms
  - escort platforms
  - forums
  - adult content platforms
- Platform classification:
  - `telegram`
  - `social`
  - `dating`
  - `sugar`
  - `adult_creator`
  - `escort_sites`
  - `forums`
- Noise reduction (filters generic pages)
- Detection of profile-like links
- Platform presence summary (✔ / ✘)

### General
- Uses `ddgs` for more reliable search results
- JSON result export
- Deduplication of results
- Multi-query generation for higher coverage
- Scoring system to prioritize relevant results
- Designed for correlation and pattern detection workflows

## Usage

### Phone search
```bash
python search_phone.py --phone 660XXXXXXX
```

## Username search
```bash
python search_username.py --username exampleuser
```

## Example Output (Phone)
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

## Example Output (Username)
```json
{
    "username": "exampleuser",
    "platforms_detected": {
        "telegram": false,
        "social": true,
        "dating": false,
        "sugar": false,
        "adult_creator": true,
        "escort_sites": true,
        "forums": true
    },
    "results": [
        {
            "title": "Example profile",
            "link": "https://example.com/profile",
            "categories": ["social"],
            "score": 3
        }
    ]
}
```

## How It Works

### 1. Generates multiple variants of the input

- Phone:
  - Raw number
  - +34 format
  - 0034 format
  - Spaced format

- Username:
  - Direct queries
  - Platform-specific queries

### 2. Builds search queries:
- Generic queries
- Keyword-enhanced queries (escort, contactos, masajes…)
- Domain-specific queries

### 3. Retrieves results using DuckDuckGo (ddgs)

### 4. Applies filtering:
- Removes generic/category pages
- Keeps relevant domains and profile-like links
- Reduces SEO noise

### 5. Processes each result:
- Phone module:
  - Detects ad type (individual / group / duo)
  - Checks phone presence in title/link
- Username module:
  - Detects platform category
- Assigns a score based on relevance signals

### 6. Classifies results:
- High → strong match + good structure
- Medium → partial relevance
- Low → weak or noisy result

### 7. Outputs structured JSON ready for analysis

---

## Current Limitations

- Results depend on search engine behavior
- Some platforms introduce SEO-heavy noise
- Detection is based on title/link only (no full page parsing)
- Username detection is indirect (no API validation)
- No automatic correlation or clustering yet

## Roadmap

- Email OSINT module
- Correlation engine (cross phone / username / email)
- Detection of reused identities across profiles
- Pattern detection (agency / multi-profile behavior)
- Export to CSV / Excel
- Optional full-page scraping for deeper validation
- CLI interface (tool-style usage)

## Notes

This project is part of a broader OSINT workflow focused on data correlation rather than simple data collection.

The objective is to transform raw search results into structured and actionable intelligence, enabling detection of patterns across multiple platforms.
