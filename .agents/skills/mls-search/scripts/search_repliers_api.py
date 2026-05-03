#!/usr/bin/env python3
"""Search Repliers for sold comparable MLS listings by subject address."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = REPO_ROOT / ".env"
API_BASE_URL = "https://api.repliers.io"
MILES_TO_KM = 1.609344


PROPERTY_TYPE_MAP = {
    "single family home": "Single Family Home",
    "single family residential": "Single Family Home",
    "single-family detached": "Single Family Home",
    "detached": "Single Family Home",
    "house": "Single Family Home",
    "sfh": "Single Family Home",
    "townhouse": "Townhouse",
    "town house": "Townhouse",
    "townhome": "Townhouse",
    "condo": "Condominium",
    "condominium": "Condominium",
    "apartment": "Condominium",
}


class RepliersError(RuntimeError):
    pass


@dataclass(frozen=True)
class SubjectFacts:
    address: str
    property_type: str
    beds: float
    baths: float
    sqft: float
    lot_size: float | None
    latitude: float
    longitude: float
    city: str | None
    listing_type: str
    mls_number: str | None


@dataclass(frozen=True)
class ApiCriteria:
    status: str
    last_status: str
    type: str
    min_sold_date: str
    max_sold_date: str
    property_type: str
    min_beds: int
    min_baths: float
    min_sqft: int
    min_lot_size_sqft: int | None
    lat: float
    long: float
    radius_km: float
    sort_by: str
    results_per_page: int


def load_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def normalize_property_type(raw: str | None) -> str:
    if not raw:
        return ""
    key = raw.strip().lower()
    return PROPERTY_TYPE_MAP.get(key, raw.strip())


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def to_int(value: Any) -> int | None:
    number = to_float(value)
    if number is None:
        return None
    return int(number)


def first_present(data: dict[str, Any], paths: list[str]) -> Any:
    for path in paths:
        current: Any = data
        ok = True
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                ok = False
                break
            current = current[part]
        if ok and current not in (None, ""):
            return current
    return None


def format_address(listing: dict[str, Any]) -> str:
    address = listing.get("address") or {}
    if isinstance(address, str):
        return address
    parts = [
        address.get("streetNumber"),
        address.get("streetName"),
        address.get("streetSuffix"),
        address.get("city"),
        address.get("state") or address.get("province"),
        address.get("zip") or address.get("postalCode"),
    ]
    return " ".join(str(part).strip() for part in parts if part).strip()


def api_get(path: str, params: dict[str, Any], api_key: str) -> dict[str, Any]:
    query: list[tuple[str, str]] = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, list):
            query.extend((key, str(item)) for item in value)
        else:
            query.append((key, str(value)))
    url = f"{API_BASE_URL}{path}?{urlencode(query)}"
    request = Request(
        url,
        headers={
            "REPLIERS-API-KEY": api_key,
            "Accept": "application/json",
            "User-Agent": "mlsauto-repliers-client/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RepliersError(f"Repliers API returned HTTP {exc.code}: {body[:500]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RepliersError(f"Could not reach Repliers API: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RepliersError("Repliers API returned non-JSON response") from exc


def get_listings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    listings = payload.get("listings", [])
    if isinstance(listings, list):
        return [item for item in listings if isinstance(item, dict)]
    return []


def find_subject(address: str, api_key: str) -> SubjectFacts:
    fields = ",".join(
        [
            "mlsNumber",
            "address",
            "details.numBedrooms",
            "details.numBathrooms",
            "details.propertyType",
            "details.sqft",
            "details.lotSizeSqft",
            "map.lat",
            "map.long",
            "type",
        ]
    )
    payload = api_get(
        "/listings",
        {
            "search": address,
            "searchFields": "address.streetName,address.streetNumber",
            "status": ["A", "U"],
            "fields": fields,
            "resultsPerPage": 5,
        },
        api_key,
    )
    listings = get_listings(payload)
    if not listings:
        raise RepliersError(f"No Repliers listing found for subject address: {address}")

    listing = listings[0]
    details = listing.get("details") or {}
    map_data = listing.get("map") or {}
    latitude = to_float(map_data.get("lat"))
    longitude = to_float(map_data.get("long"))
    beds = to_float(first_present(listing, ["details.numBedrooms", "details.numBedroomsTotal"]))
    baths = to_float(first_present(listing, ["details.numBathrooms", "details.numBathroomsFull"]))
    sqft = to_float(details.get("sqft"))
    property_type = normalize_property_type(details.get("propertyType"))
    if None in (latitude, longitude, beds, baths, sqft) or not property_type:
        raise RepliersError("Subject listing is missing required property facts or coordinates.")

    address_data = listing.get("address") or {}
    city = address_data.get("city") if isinstance(address_data, dict) else None
    return SubjectFacts(
        address=format_address(listing) or address,
        property_type=property_type,
        beds=beds,
        baths=baths,
        sqft=sqft,
        lot_size=to_float(details.get("lotSizeSqft")),
        latitude=latitude,
        longitude=longitude,
        city=city,
        listing_type=str(listing.get("type") or "sale"),
        mls_number=str(listing.get("mlsNumber")) if listing.get("mlsNumber") else None,
    )


def build_criteria(subject: SubjectFacts, *, limit: int, today: date | None = None) -> ApiCriteria:
    return ApiCriteria(
        status="U",
        last_status="Sld",
        type=subject.listing_type or "sale",
        min_sold_date="2025-01-01",
        max_sold_date=(today or date.today()).isoformat(),
        property_type=subject.property_type,
        min_beds=max(0, math.floor(subject.beds - 1)),
        min_baths=max(0, subject.baths - 0.5),
        min_sqft=max(0, math.floor(subject.sqft * 0.7)),
        min_lot_size_sqft=max(0, math.floor(subject.lot_size * 0.7)) if subject.lot_size else None,
        lat=subject.latitude,
        long=subject.longitude,
        radius_km=round(MILES_TO_KM, 3),
        sort_by="distanceAsc",
        results_per_page=limit,
    )


def search_comparables(criteria: ApiCriteria, api_key: str) -> list[dict[str, Any]]:
    params = {
        "status": criteria.status,
        "lastStatus": criteria.last_status,
        "type": criteria.type,
        "minSoldDate": criteria.min_sold_date,
        "maxSoldDate": criteria.max_sold_date,
        "propertyType": criteria.property_type,
        "minBedrooms": criteria.min_beds,
        "minBaths": criteria.min_baths,
        "minSqft": criteria.min_sqft,
        "minLotSizeSqft": criteria.min_lot_size_sqft,
        "lat": criteria.lat,
        "long": criteria.long,
        "radius": criteria.radius_km,
        "sortBy": criteria.sort_by,
        "resultsPerPage": criteria.results_per_page,
        "fields": ",".join(
            [
                "mlsNumber",
                "address",
                "details.numBedrooms",
                "details.numBathrooms",
                "details.propertyType",
                "details.sqft",
                "details.lotSizeSqft",
                "soldPrice",
                "soldDate",
                "listPrice",
                "map.distance",
            ]
        ),
    }
    return get_listings(api_get("/listings", params, api_key))


def money(value: Any) -> str:
    number = to_float(value)
    if number is None:
        return ""
    return f"${number:,.0f}"


def number(value: Any) -> str:
    converted = to_float(value)
    if converted is None:
        return ""
    if converted == int(converted):
        return f"{int(converted):,}"
    return f"{converted:g}"


def listing_row(listing: dict[str, Any]) -> dict[str, str]:
    details = listing.get("details") or {}
    sold_price = first_present(listing, ["soldPrice", "closePrice"])
    sqft = to_float(details.get("sqft"))
    sold_price_number = to_float(sold_price)
    ppsf = sold_price_number / sqft if sold_price_number and sqft else None
    return {
        "Address": format_address(listing),
        "Sold Price": money(sold_price),
        "Sold Date": str(first_present(listing, ["soldDate", "closedDate"]) or ""),
        "Type": normalize_property_type(details.get("propertyType")),
        "Beds": number(first_present(listing, ["details.numBedrooms", "details.numBedroomsTotal"])),
        "Baths": number(first_present(listing, ["details.numBathrooms", "details.numBathroomsFull"])),
        "SqFt": number(sqft),
        "Lot Size": number(details.get("lotSizeSqft")),
        "Distance": number(first_present(listing, ["map.distance"])),
        "$/SqFt": money(ppsf),
        "MLS #": str(listing.get("mlsNumber") or ""),
    }


def print_table(rows: list[dict[str, str]]) -> None:
    headers = ["Address", "Sold Price", "Sold Date", "Type", "Beds", "Baths", "SqFt", "Lot Size", "Distance", "$/SqFt", "MLS #"]
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print("| " + " | ".join(row.get(header, "").replace("|", "\\|") for header in headers) + " |")


def print_summary(subject: SubjectFacts, criteria: ApiCriteria, rows: list[dict[str, str]], *, output_json: bool) -> None:
    if output_json:
        print(
            json.dumps(
                {
                    "subject": asdict(subject),
                    "criteria": asdict(criteria),
                    "comparables": rows,
                },
                indent=2,
            )
        )
        return

    print("Subject")
    print(json.dumps(asdict(subject), indent=2))
    print("\nCriteria")
    print(json.dumps(asdict(criteria), indent=2))
    print("\nComparables")
    if rows:
        print_table(rows)
    else:
        print("No comparable sold listings returned by Repliers for these criteria.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search Repliers API for sold comparable MLS listings.")
    parser.add_argument("address", help="Subject property address.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum comparable listings to return.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--dry-run", action="store_true", help="Find subject and print criteria without searching comparables.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env()
    api_key = os.environ.get("MLS_API_KEY")
    if not api_key:
        sys.exit(f"ERROR: MLS_API_KEY must be set in {ENV_PATH}")
    try:
        subject = find_subject(args.address, api_key)
        criteria = build_criteria(subject, limit=args.limit)
        rows = [] if args.dry_run else [listing_row(listing) for listing in search_comparables(criteria, api_key)]
    except RepliersError as exc:
        sys.exit(f"ERROR: {exc}")
    print_summary(subject, criteria, rows, output_json=args.json)


if __name__ == "__main__":
    main()
