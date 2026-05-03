---
name: mls-search
description: Run MLS comparable-property searches from a subject address. Supports browser mode, which fills the MLS Listings Residential Search form and stops before submitting, and API mode, which uses Repliers/MLS_API_KEY to retrieve comparable sold-property results. Use when the user invokes /mls-search or asks for MLS comps, Repliers API comps, sold comparable searches, or MLS form preparation.
---

# MLS Comparable Search

This skill has two backends:

- **API mode**: use Repliers/API with `MLS_API_KEY` to search and return comparable results.
- **Browser mode**: use the MLS Listings website automation to fill the Residential Search form and stop before submitting.

Prefer API mode when the user asks for API, Repliers, webservice, comparison analysis, results retrieval, or a comps table. Use browser mode when the user asks to log into MLS Listings, fill the Residential Search form, inspect the browser, or preserve fill-only behavior.

If the user does not specify a backend, ask only if it affects the outcome. Otherwise prefer API mode for retrieving results and browser mode for visual form inspection.

## Required Context

Read `references/comparison_rules.md` before deriving search criteria.

For API work, read `references/api_workflow.md`.

For browser automation work, read `references/browser_workflow.md`.

## Script Entry Points

- `scripts/search.py`: MLS Listings browser automation. It fills the form and stops before submitting.
- `scripts/search_repliers_api.py`: Repliers-backed sold comparable search using `MLS_API_KEY`.

Do not print `.env` secrets. If adding dependencies, run `uv add <package>` from `/Users/xiang/projects/mlsauto`.
