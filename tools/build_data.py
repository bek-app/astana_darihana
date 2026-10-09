"""Overpass JSON -> data.js (карта оқитын нүктелер тізімі).

Қолдану: python3 -I tools/build_data.py overpass.json data.js
OSM-де мекенжайы жоқ нүктелерге tools/addresses.json кэші қолданылады (tools/geocode.py жасайды).
"""
import json
import os
import sys

src, dst = sys.argv[1], sys.argv[2]

with open(src, encoding="utf-8") as f:
    elements = json.load(f)["elements"]

geocoded = {}
cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addresses.json")
if os.path.exists(cache):
    with open(cache, encoding="utf-8") as f:
        geocoded = json.load(f)

places = []
for el in elements:
    tags = el.get("tags", {})
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lon = el.get("lon") or el.get("center", {}).get("lon")
    if lat is None or lon is None:
        continue

    street = tags.get("addr:street", "")
    house = tags.get("addr:housenumber", "")
    key = f"{el['type'][0]}{el['id']}"
    address = ", ".join(p for p in (street, house) if p) or geocoded.get(key, "")

    places.append({
        "id": key,
        "name": tags.get("name:kk") or tags.get("name") or tags.get("brand") or "Дәріхана",
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "address": address,
        "hours": tags.get("opening_hours", ""),
        "phone": tags.get("contact:phone") or tags.get("phone", ""),
    })

places.sort(key=lambda p: p["name"].lower())

with open(dst, "w", encoding="utf-8") as f:
    f.write("// OpenStreetMap дерегі (ODbL). tools/build_data.py арқылы жасалған.\n")
    f.write("const PLACES = ")
    json.dump(places, f, ensure_ascii=False, indent=1)
    f.write(";\n")

total = len(places)
print(f"нүкте: {total}")
for key in ("address", "hours", "phone"):
    print(f"  {key}: {sum(1 for p in places if p[key])}")
print(f"  24/7: {sum(1 for p in places if p['hours'].replace(' ', '') == '24/7')}")
