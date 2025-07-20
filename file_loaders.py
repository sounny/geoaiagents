import json
import csv
import io
import xml.etree.ElementTree as ET
import requests


def _table(coords):
    lines = ["| Latitude | Longitude |", "|---------:|----------:|"]
    for lat, lon in coords:
        lines.append(f"| {lat} | {lon} |")
    return "\n".join(lines)


def load_geojson(geojson: str) -> str:
    """Parse GeoJSON text and return a markdown table of point coordinates."""
    coords = []
    try:
        data = json.loads(geojson)
    except Exception:
        return _table(coords)

    def extract(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "Point":
                c = obj.get("coordinates", [])
                if len(c) >= 2:
                    lon, lat = c[:2]
                    coords.append((lat, lon))
            elif obj.get("type") == "FeatureCollection":
                for f in obj.get("features", []):
                    extract(f.get("geometry"))
            elif obj.get("type") == "Feature":
                extract(obj.get("geometry"))
            else:
                for v in obj.values():
                    extract(v)
        elif isinstance(obj, list):
            if len(obj) >= 2 and all(isinstance(n, (int, float)) for n in obj[:2]):
                lon, lat = obj[:2]
                coords.append((lat, lon))
            else:
                for v in obj:
                    extract(v)

    extract(data)
    return _table(coords)


def load_kml(kml: str) -> str:
    """Parse KML text and return a markdown table of coordinates."""
    coords = []
    try:
        root = ET.fromstring(kml)
    except Exception:
        return _table(coords)
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    for node in root.findall('.//k:coordinates', ns):
        if node.text:
            for item in node.text.strip().split():
                parts = item.split(',')
                if len(parts) >= 2:
                    lon, lat = parts[:2]
                    try:
                        coords.append((float(lat), float(lon)))
                    except ValueError:
                        continue
    return _table(coords)


def load_csv(csv_text: str) -> str:
    """Parse CSV text and return a markdown table of coordinates."""
    coords = []
    f = io.StringIO(csv_text)
    try:
        reader = csv.DictReader(f)
    except Exception:
        return _table(coords)
    if not reader.fieldnames:
        return _table(coords)
    lat_field = None
    lon_field = None
    for name in reader.fieldnames:
        lname = name.lower()
        if lname in ("lat", "latitude", "y") and lat_field is None:
            lat_field = name
        if lname in ("lon", "lng", "longitude", "x") and lon_field is None:
            lon_field = name
    if not lat_field or not lon_field:
        return _table(coords)
    for row in reader:
        try:
            lat = float(row[lat_field])
            lon = float(row[lon_field])
        except (ValueError, KeyError):
            continue
        coords.append((lat, lon))
    return _table(coords)


def fetch_geo_boundaries(iso: str, adm: str = "ADM0") -> str:
    """Download simplified boundaries from geoBoundaries and return a table."""
    url = f"https://www.geoboundaries.org/api/current/gbOpen/{iso.upper()}/{adm}/"
    try:
        info = requests.get(url, timeout=10)
        info.raise_for_status()
        data = info.json()
        g_url = data.get("simplifiedGeometryGeoJSON")
        if not g_url:
            return _table([])
        geo = requests.get(g_url, timeout=10)
        geo.raise_for_status()
    except Exception:
        return _table([])
    return load_geojson(geo.text)
