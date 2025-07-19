import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, Any


def load_geojson(path: str) -> Dict[str, Any]:
    """Load a GeoJSON file and return the parsed object."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_kml(path: str) -> Dict[str, Any]:
    """Parse a minimal subset of KML as GeoJSON."""
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    tree = ET.parse(path)
    root = tree.getroot()
    features = []
    for placemark in root.findall(".//kml:Placemark", ns):
        coords = placemark.find(".//kml:coordinates", ns)
        name = placemark.find("kml:name", ns)
        if coords is None:
            continue
        first = coords.text.strip().split()[0].split(",")
        lon, lat = float(first[0]), float(first[1])
        features.append({
            "type": "Feature",
            "properties": {"name": name.text if name is not None else ""},
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
        })
    return {"type": "FeatureCollection", "features": features}


def load_csv(path: str) -> Dict[str, Any]:
    """Load a CSV with 'lat' and 'lon' columns as GeoJSON."""
    features = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row.get("lat") or row.get("latitude"))
                lon = float(row.get("lon") or row.get("longitude"))
            except (TypeError, ValueError):
                continue
            features.append({
                "type": "Feature",
                "properties": {k: v for k, v in row.items()},
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            })
    return {"type": "FeatureCollection", "features": features}
