"""EXTRACT: discover candidate places from OpenStreetMap (free) and optionally
match them to Foursquare for extra signal (categories, popularity)."""

from __future__ import annotations

import difflib
import math

import httpx
from loguru import logger

from .models import POI

# (OSM key, value regex, our category). Order matters: first match wins.
CATEGORY_RULES: list[tuple[str, str, str]] = [
    ("boundary", "national_park|protected_area", "nature_reserve"),
    ("leisure", "nature_reserve", "nature_reserve"),
    ("natural", "wood", "forest"),
    ("landuse", "forest", "forest"),
    ("leisure", "garden", "garden"),
    ("leisure", "park", "park"),
    ("tourism", "viewpoint", "viewpoint"),
    ("natural", "peak|hill", "viewpoint"),
    ("natural", "waterfall", "waterfall"),
    ("water", "lake|reservoir", "lake"),
    ("tourism", "museum", "museum"),
    ("tourism", "gallery", "gallery"),
    ("amenity", "arts_centre", "gallery"),
    ("route", "hiking", "trail"),
    ("highway", "path", "trail"),
    ("amenity", "cafe", "cafe"),
    ("amenity", "library", "library"),
]


def build_overpass_query(bbox: tuple[float, float, float, float], timeout: int = 90) -> str:
    """Named places in the bbox that can host a restorative outing.

    bbox is (south, west, north, east), which is what Overpass expects.
    """
    s, w, n, e = bbox
    if not (-90 <= s < n <= 90 and -180 <= w < e <= 180):
        raise ValueError(f"bbox must be (south, west, north, east), got {bbox}")
    b = f"{s},{w},{n},{e}"
    selectors = [
        'nwr["leisure"~"^(park|garden|nature_reserve)$"]["name"]',
        'nwr["boundary"~"^(national_park|protected_area)$"]["name"]',
        'nwr["natural"~"^(wood|peak|hill|waterfall)$"]["name"]',
        'nwr["landuse"="forest"]["name"]',
        'nwr["tourism"~"^(viewpoint|museum|gallery)$"]["name"]',
        'nwr["amenity"~"^(arts_centre|library)$"]["name"]',
        'nwr["water"~"^(lake|reservoir)$"]["name"]',
        'relation["route"="hiking"]["name"]',
    ]
    body = "".join(f"{sel}({b});" for sel in selectors)
    return f"[out:json][timeout:{timeout}];({body});out center tags;"


def categorise(tags: dict[str, str]) -> str | None:
    import re

    for key, pattern, cat in CATEGORY_RULES:
        v = tags.get(key)
        if v and re.fullmatch(pattern, v):
            return cat
    return None


def parse_overpass(data: dict, max_places: int | None = None) -> list[POI]:
    seen: set[str] = set()
    out: list[POI] = []
    for el in data.get("elements", []):
        tags = el.get("tags") or {}
        name = tags.get("name")
        lat = el.get("lat", (el.get("center") or {}).get("lat"))
        lon = el.get("lon", (el.get("center") or {}).get("lon"))
        cat = categorise(tags)
        if not name or lat is None or lon is None or cat is None:
            continue
        key = f"{el['type']}/{el['id']}"
        dedupe = f"{name.lower()}|{round(lat, 3)}|{round(lon, 3)}"
        if key in seen or dedupe in seen:
            continue
        seen.update({key, dedupe})
        out.append(POI(osm_id=key, name=name, latitude=lat, longitude=lon, category=cat, tags=tags))
    logger.info(f"Parsed {len(out)} candidate places from {len(data.get('elements', []))} OSM elements")
    return out[:max_places] if max_places else out


def fetch_osm(query: str, url: str, client: httpx.Client | None = None) -> dict:
    c = client or httpx.Client(timeout=120, headers={"User-Agent": "serenescapes-etl/0.1"})
    r = c.post(url, data={"data": query})
    r.raise_for_status()
    return r.json()


# ---------------- Foursquare (optional) ----------------

def _dist_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dx = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    dy = math.radians(lat2 - lat1)
    return 6371000 * math.hypot(dx, dy)


def best_match(poi: POI, candidates: list[dict], max_m: float = 400, min_ratio: float = 0.75) -> dict | None:
    """Entity resolution: same place if names are similar AND locations are close."""
    best, best_score = None, 0.0
    for c in candidates:
        name = (c.get("name") or "").lower()
        ratio = difflib.SequenceMatcher(None, poi.name.lower(), name).ratio()
        lat = c.get("latitude") or ((c.get("geocodes") or {}).get("main") or {}).get("latitude")
        lon = c.get("longitude") or ((c.get("geocodes") or {}).get("main") or {}).get("longitude")
        if lat is None or lon is None:
            continue
        if ratio >= min_ratio and _dist_m(poi.latitude, poi.longitude, lat, lon) <= max_m and ratio > best_score:
            best, best_score = c, ratio
    return best


def enrich_foursquare(pois: list[POI], api_key: str, url: str, api_version: str,
                      client: httpx.Client | None = None) -> list[POI]:
    if not api_key:
        logger.info("No FOURSQUARE_API_KEY: skipping Foursquare enrichment")
        return pois
    c = client or httpx.Client(timeout=30)
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json",
               "X-Places-Api-Version": api_version}
    matched = 0
    for p in pois:
        try:
            r = c.get(url, headers=headers, params={
                "query": p.name, "ll": f"{p.latitude},{p.longitude}", "radius": 500, "limit": 5})
            r.raise_for_status()
            m = best_match(p, r.json().get("results", []))
            if m:
                p.foursquare = {"id": m.get("fsq_place_id") or m.get("fsq_id"),
                                "categories": [x.get("name") for x in m.get("categories", [])],
                                "popularity": m.get("popularity")}
                matched += 1
        except httpx.HTTPError as e:
            logger.warning(f"Foursquare lookup failed for {p.name}: {e}")
    logger.info(f"Foursquare matched {matched}/{len(pois)} places")
    return pois
