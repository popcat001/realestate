# Real Estate Automation Agent Instructions

This repository automates MLS Listings Residential Search form filling. Preserve the fill-only behavior unless the user explicitly asks for submission or result scraping.

## Project Context

- Main script: `mls_auto/search.py`
- Credentials: `mls_auto/.env` with `userid` and `pw`
- Requirement source: `prd.md`
- UI references: `residential_search.png` and `address_input.png`
- Claude skill location, when relevant: `/Users/xiang/.claude/SKILLS/mls-search/skill.md`

## Operating Rules

- Read `prd.md`, `README.md`, and the relevant script sections before changing behavior.
- Keep changes scoped. Do not refactor unrelated browser automation or debug helpers.
- Preserve local user files and credentials. Never print or commit `.env` contents.
- Do not track `.chat`; it is ignored and should remain local.
- Save a short markdown plan in the project directory for multi-step or risky work.
- Use `rg`/`rg --files` for discovery.
- Use `uv add <package>` for Python dependencies. Do not use `uv pip install`.

## MLS Workflow

The expected agent workflow is:

1. Given an address, use Zillow or Redfin to determine property type, beds, baths, SqFt, and lot size.
2. Run `mls_auto/search.py --dry-run` with those facts to verify the derived criteria.
3. Run `mls_auto/search.py` in a visible browser to log in and fill the MLS form.
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
python3 -c "compile(open('mls_auto/search.py').read(), 'mls_auto/search.py', 'exec'); print('syntax ok')"
python3 mls_auto/search.py --dry-run "1390 Miravalle Ave Los Altos CA" "Single Family Home" --beds 3 --baths 2 --sqft 1800 --lot-size 7000
```

Live MLS verification may require elevated browser permission and valid credentials.
