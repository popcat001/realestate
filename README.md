# Real Estate MLS Search Automation

This project automates filling the MLS Listings Residential Search form for comparable sold-property searches.

The workflow is intentionally fill-only: the script opens MLS in Chromium, logs in, fills the search parameters, confirms the map-address suggestion when possible, and stops before submitting the search so the user can inspect or adjust the form.

## Files

- `prd.md`: Original requirement notes.
- `residential_search.png`: Reference screenshot for the MLS Residential Search form.
- `address_input.png`: Reference screenshot for the Map Search address suggestion behavior.
- `mls_auto/search.py`: Main Playwright automation.
- `mls_auto/debug_page.py`: Login/search-page debug helper.
- `mls_auto/.env`: Local MLS credentials. This file is ignored by Git.

## Setup

Use Python 3 with Playwright and python-dotenv installed. Add Python dependencies with `uv add` so the project manifest and lockfile stay in sync:

```bash
uv add playwright python-dotenv
uv run playwright install chromium
```

Create `mls_auto/.env` with MLS credentials:

```bash
userid=YOUR_USER_ID
pw=YOUR_PASSWORD
```

Do not commit `.env` or `.chat` files.

## Usage

First, look up the subject property on Zillow or Redfin and record:

- Property type: `Single Family Home`, `Townhouse`, or `Condominium`
- Beds
- Baths
- SqFt
- Lot size in square feet

Run a dry run to verify the criteria that will be filled:

```bash
python3 mls_auto/search.py --dry-run \
  "1390 Miravalle Ave Los Altos CA" \
  "Single Family Home" \
  --beds 3 \
  --baths 2 \
  --sqft 1800 \
  --lot-size 7000
```

Open a visible browser and fill the MLS form:

```bash
python3 mls_auto/search.py \
  "1390 Miravalle Ave Los Altos CA" \
  "Single Family Home" \
  --beds 3 \
  --baths 2 \
  --sqft 1800 \
  --lot-size 7000
```

The browser stays open until Enter is pressed in the terminal. The search is not submitted.

For non-interactive checks only:

```bash
python3 mls_auto/search.py --headless --no-pause \
  "1390 Miravalle Ave Los Altos CA" \
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
python3 -c "compile(open('mls_auto/search.py').read(), 'mls_auto/search.py', 'exec'); print('syntax ok')"
python3 mls_auto/search.py --dry-run "1390 Miravalle Ave Los Altos CA" "Single Family Home" --beds 3 --baths 2 --sqft 1800 --lot-size 7000
```

Live verification requires MLS credentials and a browser session.
