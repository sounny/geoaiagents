"""Utilities for validating and parsing latitude/longitude inputs.

These helpers centralize coordinate validation so tools can share
consistent range checks and error reporting.
"""

from __future__ import annotations

import re
from typing import List, Sequence, Tuple


def is_valid_lat_lon(lat: float, lon: float) -> bool:
    """Return True if the coordinates fall within WGS84 bounds."""

    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def parse_coordinate_pairs(text: str) -> Tuple[List[Tuple[float, float]], List[Tuple[str, str]]]:
    """Parse newline- or semicolon-delimited coordinates into numeric pairs.

    Returns a tuple of (valid_pairs, invalid_entries). `invalid_entries` is a
    list of (raw_text, reason) tuples for display to the user.
    """

    pairs: List[Tuple[float, float]] = []
    invalid: List[Tuple[str, str]] = []
    lines = [line.strip() for line in re.split(r"\n|;", text or "") if line.strip()]
    for line in lines:
        parts = re.split(r"[,\s]+", line)
        if len(parts) < 2:
            invalid.append((line, "Missing latitude/longitude pair"))
            continue
        try:
            lat = float(parts[0])
            lon = float(parts[1])
        except ValueError:
            invalid.append((line, "Not a number"))
            continue
        if not is_valid_lat_lon(lat, lon):
            invalid.append((line, "Out of range (-90 <= lat <= 90, -180 <= lon <= 180)"))
            continue
        pairs.append((lat, lon))
    return pairs, invalid


def format_invalid_notes(invalid_entries: Sequence[Tuple[str, str]]) -> str:
    """Render invalid coordinate notes as a markdown bullet list."""

    if not invalid_entries:
        return ""
    lines = ["", "_Skipped invalid inputs:_"]
    for raw, reason in invalid_entries:
        lines.append(f"- `{raw}` ({reason})")
    return "\n".join(lines)
