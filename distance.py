"""Distance calculation utilities for coordinate pairs."""

from __future__ import annotations

import math
import re
from typing import List, Sequence, Tuple

from validation import format_invalid_notes, is_valid_lat_lon


def _parse_distance_pairs(
    text: str,
) -> Tuple[List[Tuple[float, float, float, float]], List[Tuple[str, str]]]:
    pairs: List[Tuple[float, float, float, float]] = []
    invalid: List[Tuple[str, str]] = []
    lines = [line.strip() for line in re.split(r"\n|;", text or "") if line.strip()]
    for line in lines:
        parts = re.split(r"[,\s]+", line)
        if len(parts) < 4:
            invalid.append((line, "Expected lat1, lon1, lat2, lon2"))
            continue
        try:
            lat1, lon1, lat2, lon2 = map(float, parts[:4])
        except ValueError:
            invalid.append((line, "Not a number"))
            continue
        if not is_valid_lat_lon(lat1, lon1):
            invalid.append((line, "Point A out of range (-90 <= lat <= 90, -180 <= lon <= 180)"))
            continue
        if not is_valid_lat_lon(lat2, lon2):
            invalid.append((line, "Point B out of range (-90 <= lat <= 90, -180 <= lon <= 180)"))
            continue
        pairs.append((lat1, lon1, lat2, lon2))
    return pairs, invalid


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
        delta_lambda / 2.0
    ) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def calculate_distance(coordinates: str) -> str:
    """Calculate great-circle distances between coordinate pairs.

    Input format: newline or semicolon separated lat1,lon1,lat2,lon2.
    """

    pairs, invalid = _parse_distance_pairs(coordinates)
    if not pairs:
        return "No valid coordinate pairs provided." + format_invalid_notes(invalid)
    lines: List[str] = [
        "| Point A Lat | Point A Lon | Point B Lat | Point B Lon | Distance (km) | Distance (mi) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for lat1, lon1, lat2, lon2 in pairs:
        distance_km = _haversine_km(lat1, lon1, lat2, lon2)
        distance_mi = distance_km * 0.621371
        lines.append(
            "| {lat1:.6f} | {lon1:.6f} | {lat2:.6f} | {lon2:.6f} | {km:.2f} | {mi:.2f} |".format(
                lat1=lat1,
                lon1=lon1,
                lat2=lat2,
                lon2=lon2,
                km=distance_km,
                mi=distance_mi,
            )
        )
    return "\n".join(lines) + format_invalid_notes(invalid)


def main() -> None:
    user_input = input(
        "Enter coordinate pairs as lat1,lon1,lat2,lon2 (newline or semicolon separated):\n"
    )
    print(calculate_distance(user_input))


if __name__ == "__main__":
    main()
