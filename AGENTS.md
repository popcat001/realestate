# Real Estate Automation Agent Instructions

This repository automates MLS comparable-property searches through either Repliers API search or MLS Listings Residential Search form filling. Preserve browser fill-only behavior unless the user explicitly asks for submission or result scraping.

## Project Context

- Browser script: `skills/mls-search/scripts/search.py`
- API script: `skills/mls-search/scripts/search_repliers_api.py`
- Credentials: `.env` with `userid` and `pw` for browser mode, plus `MLS_API_KEY` for API mode
- Requirement source: `prd.md`
- UI references: `skills/mls-search/assets/residential_search.png` and `skills/mls-search/assets/address_input.png`
- Local skill location: `skills/mls-search/SKILL.md`

## Operating Rules

- Read `prd.md`, `README.md`, and the relevant script sections before changing behavior.
- Keep changes scoped. Do not refactor unrelated browser automation or debug helpers.
- Preserve local user files and credentials. Never print or commit `.env` contents.
- Do not track `.chat`; it is ignored and should remain local.
- Save a short markdown plan in the project directory for multi-step or risky work.
- Use `rg`/`rg --files` for discovery.
- Use `uv add <package>` for Python dependencies. Do not use `uv pip install`.

## MLS Workflow

Prefer API mode when the user asks to use Repliers/API, avoid browser login, retrieve results, or build comparison analysis:

```bash
python3 skills/mls-search/scripts/search_repliers_api.py "990 Rose Ave, Mountain View, CA 94040"
```

The expected browser workflow is:

1. Given an address, use Zillow or Redfin to determine property type, beds, baths, SqFt, and lot size.
2. Run `skills/mls-search/scripts/search.py --dry-run` with those facts to verify the derived criteria.
3. Run `skills/mls-search/scripts/search.py` in a visible browser to log in and fill the MLS form.
4. Stop before submitting. Let the user inspect the browser.

The script should fill:

- Status: `Sold`
- Sale Date: `01/01/2025` through today
- Property Type: Zillow/Redfin property type
- Beds: subject beds minus `1`, with `+`
- Baths: subject baths minus `0.5`, with `+`
- SqFt: subject SqFt times `0.7`, with `+`
- Lot Size: subject lot size times `0.7`, with `+`
- Map Search: within `1` mile of the address

## Browser Testing

- Use a visible browser when the user asks to test or inspect the MLS form.
- Use `--headless --no-pause` only for non-interactive smoke checks.
- MLS Map Search requires confirming the `Did you mean:` suggestion. If automation cannot click it reliably, leave the browser open and tell the user to click the suggestion text manually.

## Verification

At minimum, run:

```bash
python3 -c "compile(open('skills/mls-search/scripts/search.py').read(), 'skills/mls-search/scripts/search.py', 'exec'); print('syntax ok')"
python3 -c "compile(open('skills/mls-search/scripts/search_repliers_api.py').read(), 'skills/mls-search/scripts/search_repliers_api.py', 'exec'); print('syntax ok')"
python3 skills/mls-search/scripts/search.py --dry-run "990 Rose Ave, Mountain View, CA 94040" "Single Family Home" --beds 3 --baths 2 --sqft 1800 --lot-size 7000
```

Live browser verification may require elevated browser permission and valid credentials. Live API verification requires `MLS_API_KEY`.
