"""Мекенжайы жоқ нүктелерге Nominatim арқылы мекенжай табады (кэш: addresses.json).

Қолдану: python3 -I tools/geocode.py overpass.json tools/addresses.json
Nominatim ережесі бойынша секундына бір сұраныстан артық жіберілмейді.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

src, dst = sys.argv[1], sys.argv[2]

with open(src, encoding="utf-8") as f:
    elements = json.load(f)["elements"]

cache = {}
if os.path.exists(dst):
    with open(dst, encoding="utf-8") as f:
        cache = json.load(f)

for el in elements:
    tags = el.get("tags", {})
    key = f"{el['type'][0]}{el['id']}"
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lon = el.get("lon") or el.get("center", {}).get("lon")
    if key in cache or tags.get("addr:street") or lat is None or lon is None:
        continue

    query = urllib.parse.urlencode({
        "format": "jsonv2", "lat": lat, "lon": lon,
        "zoom": 18, "addressdetails": 1, "accept-language": "kk",
    })
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/reverse?{query}",
        headers={"User-Agent": "astana-gis-pharmacy-map/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            addr = json.load(res).get("address", {})
    except Exception as err:
        print(f"{key}: {err}")
        time.sleep(1.1)
        continue

    cache[key] = ", ".join(p for p in (addr.get("road", ""), addr.get("house_number", "")) if p)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    time.sleep(1.1)

print(f"кэште: {len(cache)}, мекенжайы бар: {sum(1 for v in cache.values() if v)}")
