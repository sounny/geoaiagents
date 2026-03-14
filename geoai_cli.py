"""Unified command-line interface for GeoAI Agents."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from tool_registry import create_registry

SYSTEM_PROMPT = (
    "You are a GeoAI Agent who is an expert GIS and Remote Sensing Analyst, "
    "cartographer, and Geospatial Developer. Your name is Humboldt, in honor "
    "of Alexander von Humboldt, the father of Modern Geography. You must "
    "always use the provided function tools to perform geospatial tasks and "
    "never guess results. When you invoke a tool it will be logged for the "
    "user to see. If the user requests a map marker or location to be shown, "
    "call `geocode_locations` first so the interface can display the point."
)

TEXT_FIELD_BY_TOOL = {
    "load_geojson": "geojson",
    "load_kml": "kml",
    "load_csv": "csv",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="GeoAI CLI with direct geospatial tools and optional LLM chat mode."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("HUMBOLDT_DEBUG", "0") in ("1", "true", "True"),
        help="Enable debug logging.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-tools", help="List all registered tools and exit.")

    run_tool = subparsers.add_parser("run-tool", help="Run any registered tool by name.")
    run_tool.add_argument("tool_name", help="Registered tool name.")
    run_tool.add_argument(
        "--payload",
        default="",
        help="Primary string payload for the tool (locations/coordinates/text depending on tool).",
    )
    run_tool.add_argument(
        "--adm",
        default="ADM0",
        help="Administrative level for fetch_geo_boundaries (default ADM0).",
    )

    for cmd_name, help_text in [
        ("geocode", "Geocode newline/semicolon-separated locations."),
        ("reverse", "Reverse geocode lat,lon pairs."),
        ("dms", "Convert decimal degree lat,lon pairs to DMS."),
        ("distance", "Compute haversine distances from lat1,lon1,lat2,lon2 pairs."),
    ]:
        cmd = subparsers.add_parser(cmd_name, help=help_text)
        cmd.add_argument(
            "value",
            nargs="?",
            default="",
            help="Input text. If omitted, stdin is used.",
        )

    boundaries = subparsers.add_parser(
        "boundaries",
        help="Fetch boundary centroids from geoBoundaries by ISO code.",
    )
    boundaries.add_argument("iso", help="ISO 3166-1 alpha-3 code, e.g., USA")
    boundaries.add_argument("--adm", default="ADM0", help="Admin level (ADM0/ADM1/...)" )

    chat = subparsers.add_parser(
        "chat",
        help="Start interactive LLM + tool calling chat (Humboldt mode).",
    )
    chat.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_BASE_URL", "http://localhost:5272/v1/"),
        help="OpenAI API base URL.",
    )
    chat.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY", "unused"),
        help="OpenAI API key.",
    )
    chat.add_argument(
        "--model",
        default=(
            os.getenv("OPENAI_MODEL")
            or os.getenv("HUMBOLDT_MODEL")
            or "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
        ),
        help="Model name.",
    )
    chat.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("HUMBOLDT_MAX_STEPS", 3)),
        help="Maximum consecutive tool calls per user turn.",
    )

    return parser


def _read_value_or_stdin(value: str) -> str:
    if value:
        return value
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def _tool_args_for(tool_name: str, payload: str, adm: str = "ADM0") -> dict:
    if tool_name == "geocode_locations":
        return {"locations": payload}
    if tool_name in {"convert_dd_to_dms", "reverse_geocode_coordinates", "calculate_distance"}:
        return {"coordinates": payload}
    if tool_name in TEXT_FIELD_BY_TOOL:
        return {TEXT_FIELD_BY_TOOL[tool_name]: payload}
    if tool_name == "fetch_geo_boundaries":
        return {"iso": payload, "adm": adm}
    return {"input": payload}


def _run_tool_command(args: argparse.Namespace, registry) -> int:
    if args.command == "geocode":
        payload = _read_value_or_stdin(args.value)
        print(registry.invoke("geocode_locations", {"locations": payload}) or "")
        return 0
    if args.command == "reverse":
        payload = _read_value_or_stdin(args.value)
        print(registry.invoke("reverse_geocode_coordinates", {"coordinates": payload}) or "")
        return 0
    if args.command == "dms":
        payload = _read_value_or_stdin(args.value)
        print(registry.invoke("convert_dd_to_dms", {"coordinates": payload}) or "")
        return 0
    if args.command == "distance":
        payload = _read_value_or_stdin(args.value)
        print(registry.invoke("calculate_distance", {"coordinates": payload}) or "")
        return 0
    if args.command == "boundaries":
        print(registry.invoke("fetch_geo_boundaries", {"iso": args.iso, "adm": args.adm}) or "")
        return 0
    if args.command == "run-tool":
        payload = args.payload
        if not payload and not sys.stdin.isatty():
            payload = sys.stdin.read().strip()
        tool_args = _tool_args_for(args.tool_name, payload, args.adm)
        result = registry.invoke(args.tool_name, tool_args)
        if result is None:
            print(f"Unknown tool: {args.tool_name}")
            return 2
        print(result)
        return 0
    return 1


def _run_chat_mode(args: argparse.Namespace, registry) -> int:
    from openai import OpenAI

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    functions = registry.openai_functions()

    print("Hi, I'm Humboldt CLI. Type 'exit' to quit.")
    while True:
        user_input = input("geoai> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            return 0
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        steps = 0

        while steps <= args.max_steps:
            response = client.chat.completions.create(
                model=args.model,
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=1000,
                frequency_penalty=1,
            )
            message = response.choices[0].message
            call = getattr(message, "function_call", None)
            if call:
                if args.debug:
                    print(f"[DEBUG] Tool requested: {call.name} {call.arguments}")
                tool_output = registry.invoke(call.name, call.arguments) or ""
                messages.append({"role": "assistant", "content": None, "function_call": call})
                messages.append({"role": "function", "name": call.name, "content": tool_output})
                steps += 1
                continue

            if message.content:
                print(message.content)
                messages.append({"role": "assistant", "content": message.content})
            break

        if steps > args.max_steps:
            print("[INFO] Reached max tool-call steps for this turn.")

        if len(messages) > 30:
            messages = [messages[0]] + messages[-29:]


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    registry = create_registry()

    if args.command == "list-tools":
        for tool in registry.openai_functions():
            print(f"- {tool['name']}: {tool['description']}")
        return 0

    if args.command == "chat":
        return _run_chat_mode(args, registry)

    if args.command in {"geocode", "reverse", "dms", "distance", "boundaries", "run-tool"}:
        return _run_tool_command(args, registry)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
