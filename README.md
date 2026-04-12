# OSINT Phone Correlator

Tool for automating phone number OSINT investigations and preparing data for correlation analysis.

## Features

- Search phone numbers across multiple platforms
- Custom search queries (escort-related, specific sites)
- Uses `ddgs` for more reliable search results
- JSON result export
- Basic deduplication and noise filtering
- Designed for future correlation and pattern detection

## Usage

```bash
python search.py --phone 660XXXXXXX
```

## Example Output
```json
[
    {
        "query": "\"660XXXXXXX\"",
        "title": "Example listing",
        "link": "https://example.com"
    }
]
```

## Current Limitations
- Search results may vary depending on engine behavior
- Some queries may return noise or limited data
- No advanced correlation or scoring implemented yet

## Roadmap
- Domain-based correlation
- Result scoring (relevance / risk)
- Detection of reused phone numbers across platforms
- Export to CSV for data analysis

## Notes
This project is under active development and is part of a broader OSINT workflow focused on data correlation rather than simple data collection.
