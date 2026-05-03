# Browser Workflow

Use this workflow when the user asks to prepare or inspect the MLS Listings Residential Search form.

Preserve fill-only behavior. The browser workflow should not submit the MLS search or claim comparable-sale results unless the user explicitly asks for submission and results review.

## Verify Criteria

Run a dry run first so the selected criteria are visible before MLS login:

```bash
python3 /Users/xiang/projects/mlsauto/skills/mls-search/scripts/search.py \
  "<full address>" "<property_type>" \
  --beds <beds> --baths <baths> --sqft <sqft> --lot-size <lot_size> \
  --dry-run
```

Confirm the dry-run output follows the requirement:

- Status is `Sold`
- Sale Date is `01/01/2025` through today
- Beds is `(subject beds - 1)+`
- Baths is `(subject baths - 0.5)+`
- SqFt is `(subject sqft * 0.7)+`
- Lot Size is `(subject lot size * 0.7)+`
- Map Search uses `1` mile and the provided address

## Fill MLS Form

Run the visible browser command:

```bash
python3 /Users/xiang/projects/mlsauto/skills/mls-search/scripts/search.py \
  "<full address>" "<property_type>" \
  --beds <beds> --baths <baths> --sqft <sqft> --lot-size <lot_size>
```

Where `<property_type>` is one of: `Single Family Home`, `Townhouse`, `Condominium`.

For automated non-interactive verification only, add `--headless --no-pause`. When the user asks to test or inspect the form, do not use headless mode; keep the browser open.

The script will:

- Open a Chromium browser
- Log into mlslistings.com with credentials from `.env`
- Navigate to the Residential Search form
- Fill in: Status=Sold, Sale Date 2025-01-01 to today, Property Type
- Fill Building Description using derived lower bounds with `+` suffix: Beds, Tot Baths, SqFt, Lot Size
- Map Search: within 1 mile of the address
- Type the address and click the visible MLS address suggestion when it appears
- Stop before submitting so the user can visually inspect or adjust the filled parameters

If the MLS form changes and a field cannot be found, the script should stop with a clear `RuntimeError` instead of silently leaving criteria incomplete.
