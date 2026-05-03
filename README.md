# Real Estate MLS Search Automation

This project automates MLS comparable sold-property searches from a subject address. The API workflow uses Repliers with `MLS_API_KEY` to find the subject property, derive the sold-comps criteria, search nearby sold listings, and return comparison results as a table or JSON.

The browser workflow remains available for MLS Listings form inspection: it opens Chromium, logs in, fills the search parameters, confirms the map-address suggestion when possible, and stops before submitting.

## Files

- `prd.md`: Original requirement notes.
- `skills/mls-search/assets/residential_search.png`: Reference screenshot for the MLS Residential Search form.
- `skills/mls-search/assets/address_input.png`: Reference screenshot for the Map Search address suggestion behavior.
- `skills/mls-search/scripts/search.py`: Main Playwright automation.
- `skills/mls-search/scripts/search_repliers_api.py`: Repliers API comparable-search CLI.
- `skills/mls-search/SKILL.md`: Local skill entrypoint for browser and API MLS search workflows.
- `.env`: Local MLS credentials. This file is ignored by Git.

## Setup

Use Python 3 with Playwright and python-dotenv installed. Add Python dependencies with `uv add` so the project manifest and lockfile stay in sync:

```bash
uv add playwright python-dotenv
uv run playwright install chromium
```

Create `.env` with MLS credentials:

```bash
userid=YOUR_USER_ID
pw=YOUR_PASSWORD
MLS_API_KEY=YOUR_REPLIERS_API_KEY
```

Do not commit `.env` or `.chat` files.

## Usage

### API Comparable Search

Use the Repliers API path when you want comparable sold-property results without logging into the MLS website:

```bash
python3 skills/mls-search/scripts/search_repliers_api.py \
  "990 Rose Ave, Mountain View, CA 94040"
```

For JSON output:

```bash
python3 skills/mls-search/scripts/search_repliers_api.py \
  "990 Rose Ave, Mountain View, CA 94040" \
  --json --limit 10
```

The script loads `MLS_API_KEY` from `.env`, finds the subject property by address, derives sold-comparable criteria, and queries Repliers for sold listings within 1 mile.

### Browser Form Fill

First, look up the subject property on Zillow or Redfin and record:

- Property type: `Single Family Home`, `Townhouse`, or `Condominium`
- Beds
- Baths
- SqFt
- Lot size in square feet

Run a dry run to verify the criteria that will be filled:

```bash
python3 skills/mls-search/scripts/search.py --dry-run \
  "990 Rose Ave, Mountain View, CA 94040" \
  "Single Family Home" \
  --beds 3 \
  --baths 2 \
  --sqft 1800 \
  --lot-size 7000
```

Open a visible browser and fill the MLS form:

```bash
python3 skills/mls-search/scripts/search.py \
  "990 Rose Ave, Mountain View, CA 94040" \
  "Single Family Home" \
  --beds 3 \
  --baths 2 \
  --sqft 1800 \
  --lot-size 7000
```

The browser stays open until Enter is pressed in the terminal. The search is not submitted.

For non-interactive checks only:

```bash
python3 skills/mls-search/scripts/search.py --headless --no-pause \
  "990 Rose Ave, Mountain View, CA 94040" \
  "Single Family Home" \
  --beds 3 \
  --baths 2 \
  --sqft 1800 \
  --lot-size 7000
```

## Criteria Rules

The script fills:

- Status: `Sold`
- Sale Date: `01/01/2025` through today
- Property Type: value provided from Zillow/Redfin lookup
- Beds: subject beds minus `1`, with `+`
- Baths: subject baths minus `0.5`, with `+`
- SqFt: subject SqFt times `0.7`, with `+`
- Lot Size: subject lot size times `0.7`, with `+`
- Map Search: within `1` mile of the subject address

## Address Suggestion

MLS shows a `Did you mean:` suggestion after typing the Map Search address. The automation attempts to hover and click the suggestion text because the map selection is not committed by typing alone.

If the popup remains visible, manually click the suggestion text in the browser before continuing.

## Verification

Run syntax and dry-run checks after edits:

```bash
python3 -c "compile(open('skills/mls-search/scripts/search.py').read(), 'skills/mls-search/scripts/search.py', 'exec'); print('syntax ok')"
python3 -c "compile(open('skills/mls-search/scripts/search_repliers_api.py').read(), 'skills/mls-search/scripts/search_repliers_api.py', 'exec'); print('syntax ok')"
python3 skills/mls-search/scripts/search.py --dry-run "990 Rose Ave, Mountain View, CA 94040" "Single Family Home" --beds 3 --baths 2 --sqft 1800 --lot-size 7000
```

Live browser verification requires MLS credentials and a browser session. Live API verification requires `MLS_API_KEY`.
