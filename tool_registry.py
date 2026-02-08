"""Centralized tool registry and plugin loader for GeoAI agents."""

from __future__ import annotations

import importlib
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from dd2dms import convert_dd_to_dms
from distance import calculate_distance
from file_loaders import fetch_geo_boundaries, load_csv, load_geojson, load_kml
from geocode import geocode_locations, reverse_geocode_coordinates


ToolHandler = Callable[[Dict[str, Any]], str]


@dataclass
class ToolDefinition:
    """Definition for an OpenAI callable tool."""

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: ToolHandler


class ToolRegistry:
    """Registry for built-in and plugin tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        *,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: ToolHandler,
    ) -> None:
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )

    def openai_functions(self) -> list[Dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]

    def invoke(self, tool_name: str, raw_args: Any) -> Optional[str]:
        tool = self._tools.get(tool_name)
        if not tool:
            return None
        parsed = parse_tool_args(raw_args)
        try:
            return tool.handler(parsed)
        except Exception as exc:  # noqa: BLE001 - report and continue
            logging.error("Tool '%s' failed: %s", tool_name, exc)
            return f"Error running {tool_name}: {exc}"

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tools


DEFAULT_TOOL_COORD_PARSERS = {
    "geocode_locations": (2, 3),
    "convert_dd_to_dms": (0, 1),
    "reverse_geocode_coordinates": (0, 1),
    "load_geojson": (0, 1),
    "load_kml": (0, 1),
    "load_csv": (0, 1),
    "fetch_geo_boundaries": (0, 1),
    "calculate_distance": "distance",
}


def parse_tool_args(raw_args: Any) -> Dict[str, Any]:
    """Parse tool call args from JSON string or dict."""
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str):
        try:
            parsed = json.loads(raw_args or "{}")
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def create_registry() -> ToolRegistry:
    """Create registry with built-in tools and optional plugin tools."""
    registry = ToolRegistry()
    _register_builtin_tools(registry)
    _load_plugins(registry)
    return registry


def _register_builtin_tools(registry: ToolRegistry) -> None:
    registry.register_tool(
        name="geocode_locations",
        description="Geocode a list of locations and return a markdown table",
        parameters={
            "type": "object",
            "properties": {
                "locations": {
                    "type": "string",
                    "description": "Newline- or semicolon-delimited list of locations to geocode",
                }
            },
            "required": ["locations"],
        },
        handler=lambda arguments: geocode_locations(arguments.get("locations", "")),
    )
    registry.register_tool(
        name="convert_dd_to_dms",
        description="Convert decimal-degree coordinates to DMS table",
        parameters={
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "string",
                    "description": "Newline- or semicolon-delimited DD lat,lon pairs",
                }
            },
            "required": ["coordinates"],
        },
        handler=lambda arguments: convert_dd_to_dms(arguments.get("coordinates", "")),
    )
    registry.register_tool(
        name="reverse_geocode_coordinates",
        description="Reverse geocode lat/lon pairs to addresses",
        parameters={
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "string",
                    "description": "Newline- or semicolon-delimited DD lat,lon pairs",
                }
            },
            "required": ["coordinates"],
        },
        handler=lambda arguments: reverse_geocode_coordinates(arguments.get("coordinates", "")),
    )
    registry.register_tool(
        name="calculate_distance",
        description="Calculate great-circle distance between coordinate pairs",
        parameters={
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "string",
                    "description": "Newline- or semicolon-delimited lat1,lon1,lat2,lon2 pairs",
                }
            },
            "required": ["coordinates"],
        },
        handler=lambda arguments: calculate_distance(arguments.get("coordinates", "")),
    )
    registry.register_tool(
        name="load_geojson",
        description="Load GeoJSON text and return a coordinate table",
        parameters={
            "type": "object",
            "properties": {
                "geojson": {
                    "type": "string",
                    "description": "Contents of a GeoJSON file",
                }
            },
            "required": ["geojson"],
        },
        handler=lambda arguments: load_geojson(arguments.get("geojson", "")),
    )
    registry.register_tool(
        name="load_kml",
        description="Load KML text and return a coordinate table",
        parameters={
            "type": "object",
            "properties": {
                "kml": {"type": "string", "description": "Contents of a KML file"}
            },
            "required": ["kml"],
        },
        handler=lambda arguments: load_kml(arguments.get("kml", "")),
    )
    registry.register_tool(
        name="load_csv",
        description="Load CSV text with latitude/longitude columns",
        parameters={
            "type": "object",
            "properties": {
                "csv": {"type": "string", "description": "Contents of a CSV file"}
            },
            "required": ["csv"],
        },
        handler=lambda arguments: load_csv(arguments.get("csv", "")),
    )
    registry.register_tool(
        name="fetch_geo_boundaries",
        description="Download simplified political boundaries from geoBoundaries",
        parameters={
            "type": "object",
            "properties": {
                "iso": {"type": "string", "description": "ISO 3166-1 alpha-3 code"},
                "adm": {
                    "type": "string",
                    "description": "Administrative level",
                    "default": "ADM0",
                },
            },
            "required": ["iso"],
        },
        handler=lambda arguments: fetch_geo_boundaries(
            arguments.get("iso", ""),
            arguments.get("adm", "ADM0"),
        ),
    )


def _load_plugins(registry: ToolRegistry) -> None:
    """Load plugin modules from GEOAI_PLUGIN_MODULES env var.

    Plugin modules should expose `register_tools(registry)`.
    """
    plugin_modules = os.getenv("GEOAI_PLUGIN_MODULES", "").strip()
    if not plugin_modules:
        return

    for module_name in [m.strip() for m in plugin_modules.split(",") if m.strip()]:
        try:
            module = importlib.import_module(module_name)
            register_fn = getattr(module, "register_tools", None)
            if callable(register_fn):
                register_fn(registry)
                logging.info("Loaded plugin module: %s", module_name)
            else:
                logging.warning(
                    "Plugin module '%s' has no callable register_tools(registry)",
                    module_name,
                )
        except Exception as exc:  # noqa: BLE001
            logging.warning("Failed to load plugin module '%s': %s", module_name, exc)
