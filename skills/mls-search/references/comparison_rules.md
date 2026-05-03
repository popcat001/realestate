# Comparison Rules

Input: a subject property address.

Determine subject property facts from Zillow, Redfin, user-provided facts, or a structured API:

- Property type, normalized to `Single Family Home`, `Townhouse`, or `Condominium`
- Beds
- Baths
- SqFt
- Lot size in square feet

Search query examples:

- `site:zillow.com "990 Rose Ave Mountain View"`
- `site:redfin.com "990 Rose Ave, Mountain View, CA 94040"`

Property type normalization:

- **Single Family Home**: SFH, single-family, ranch, craftsman, traditional, detached homes
- **Townhouse**: townhouse, townhome, attached multi-story homes
- **Condominium**: condo, condominium, co-op, flat in a complex

Comparable-search criteria:

- Status: `Sold`
- Sale date from: `2025-01-01`
- Sale date to: today
- Property type: subject property type
- Beds minimum: `max(0, subject beds - 1)`
- Baths minimum: `max(0, subject baths - 0.5)`
- SqFt minimum: `floor(subject sqft * 0.7)`
- Lot size minimum: `floor(subject lot size * 0.7)`
- Radius: `1` mile from subject address

Browser mode should append `+` to minimum numeric fields because the MLS form expects plus behavior.
