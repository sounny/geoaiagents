"""Run this model in Python

> pip install openai
"""

import json
import argparse
import os
import logging
import subprocess
import sys
import importlib.util
from typing import Any, Dict, Optional


def check_and_install_dependencies():
    """Check if required dependencies are installed and install them if missing."""
    print("Checking dependencies...")

    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"Warning: {requirements_file} not found. Assuming dependencies are installed.")
        return

    missing_packages = []

    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (remove version specifiers)
                package_name = line.split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                if not is_package_installed(package_name):
                    missing_packages.append(line)

    if missing_packages:
        print(f"Missing packages found: {', '.join(missing_packages)}")
        print("Installing missing dependencies...")

        for package in missing_packages:
            try:
                print(f"Installing {package}...")
                # Prefer --user for managed environments
                subprocess.run([sys.executable, "-m", "pip", "install", "--user", package],
                               check=True, capture_output=True, text=True)
                print(f"✓ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {package} with --user flag")
                try:
                    print(f"Trying alternative installation for {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", package],
                                   check=True, capture_output=True, text=True)
                    print(f"✓ Successfully installed {package}")
                except subprocess.CalledProcessError as e2:
                    if e.stderr:
                        print(f"Error details: {e.stderr}")
                    if e.stdout:
                        print(f"Output: {e.stdout}")
                    print("\nAutomatic installation failed. Please install dependencies manually:")
                    print("Option 1: pip install --user -r requirements.txt")
                    print("Option 2: pip install --break-system-packages -r requirements.txt")
                    print("Option 3: Create a virtual environment:")
                    print("  python3 -m venv venv")
                    print("  source venv/bin/activate")
                    print("  pip install -r requirements.txt")
                    sys.exit(1)

        print("All dependencies installed successfully!")
    else:
        print("All dependencies are already installed.")


def is_package_installed(package_name):
    """Check if a package is installed."""
    package_mapping = {
        'openai': 'openai',
        'geopy': 'geopy'
    }
    check_name = package_mapping.get(package_name, package_name)
    try:
        spec = importlib.util.find_spec(check_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


# Import modules that are definitely available; others imported after deps

def main():
    parser = argparse.ArgumentParser(description="Interactive GeoAI agent")
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_BASE_URL", "http://localhost:5272/v1/"),
        help="OpenAI API base URL",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY", "unused"),
        help="OpenAI API key",
    )
    parser.add_argument(
        "--model",
        default=(
            os.getenv("OPENAI_MODEL")
            or os.getenv("HUMBOLDT_MODEL")
            or "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
        ),
        help="Model name to use",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip automatic dependency checking and installation",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("HUMBOLDT_MAX_STEPS", 3)),
        help="Max consecutive tool calls before stopping (default: 3)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("HUMBOLDT_DEBUG", "0") in ("1", "true", "True"),
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if not args.skip_deps:
        check_and_install_dependencies()

    # Import modules after dependency checking
    try:
        from openai import OpenAI
        from geocode import geocode_locations, reverse_geocode_coordinates
        from dd2dms import convert_dd_to_dms
        try:
            from file_loaders import (
                load_geojson,
                load_kml,
                load_csv,
                fetch_geo_boundaries,
            )
            loaders_available = True
        except Exception:
            loaders_available = False
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed by running:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    system_prompt = (
        "You are a GeoAI Agent who is an expert GIS and Remote Sensing Analyst, "
        "cartographer, and Geospatial Developer. Your name is Humboldt, in honor "
        "of Alexander von Humboldt, the father of Modern Geography. You must "
        "always use the provided function tools to perform geospatial tasks and "
        "never guess results. When you invoke a tool it will be logged for the "
        "user to see. If the user requests a map marker or location to be shown, "
        "call `geocode_locations` first so the interface can display the point. "
        "Do not claim you are unable to manipulate maps or geospatial data; use "
        "the provided tools and let the interface handle map updates."
    )

    messages = [{"role": "system", "content": system_prompt}]
    functions = [
        {
            "name": "geocode_locations",
            "description": "Geocode a list of locations and return a markdown table",
            "parameters": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited list of locations to geocode",
                    }
                },
                "required": ["locations"],
            },
        },
        {
            "name": "convert_dd_to_dms",
            "description": "Convert decimal-degree coordinates to DMS table",
            "parameters": {
                "type": "object",
                "properties": {
                    "coordinates": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited DD lat,lon pairs",
                    }
                },
                "required": ["coordinates"],
            },
        },
        {
            "name": "reverse_geocode_coordinates",
            "description": "Reverse geocode lat/lon pairs to addresses",
            "parameters": {
                "type": "object",
                "properties": {
                    "coordinates": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited DD lat,lon pairs",
                    }
                },
                "required": ["coordinates"],
            },
        },
    ]

    if 'loaders_available' in locals() and loaders_available:
        functions.extend([
            {
                "name": "load_geojson",
                "description": "Load GeoJSON text and return a coordinate table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "geojson": {
                            "type": "string",
                            "description": "Contents of a GeoJSON file",
                        }
                    },
                    "required": ["geojson"],
                },
            },
            {
                "name": "load_kml",
                "description": "Load KML text and return a coordinate table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "kml": {"type": "string", "description": "Contents of a KML file"}
                    },
                    "required": ["kml"],
                },
            },
            {
                "name": "load_csv",
                "description": "Load CSV text with latitude/longitude columns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "csv": {"type": "string", "description": "Contents of a CSV file"}
                    },
                    "required": ["csv"],
                },
            },
            {
                "name": "fetch_geo_boundaries",
                "description": "Download simplified political boundaries from geoBoundaries",
                "parameters": {
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
            },
        ])

    # Tool registry
    def tool_geocode_locations(arguments: Dict[str, Any]) -> str:
        return geocode_locations(arguments.get("locations", ""))

    def tool_convert_dd_to_dms(arguments: Dict[str, Any]) -> str:
        return convert_dd_to_dms(arguments.get("coordinates", ""))

    def tool_reverse_geocode_coordinates(arguments: Dict[str, Any]) -> str:
        return reverse_geocode_coordinates(arguments.get("coordinates", ""))

    tool_registry: Dict[str, Any] = {
        "geocode_locations": tool_geocode_locations,
        "convert_dd_to_dms": tool_convert_dd_to_dms,
        "reverse_geocode_coordinates": tool_reverse_geocode_coordinates,
    }

    if 'loaders_available' in locals() and loaders_available:
        def tool_load_geojson(arguments: Dict[str, Any]) -> str:
            return load_geojson(arguments.get("geojson", ""))

        def tool_load_kml(arguments: Dict[str, Any]) -> str:
            return load_kml(arguments.get("kml", ""))

        def tool_load_csv(arguments: Dict[str, Any]) -> str:
            return load_csv(arguments.get("csv", ""))

        def tool_fetch_geo_boundaries(arguments: Dict[str, Any]) -> str:
            return fetch_geo_boundaries(arguments.get("iso", ""), arguments.get("adm", "ADM0"))

        tool_registry.update({
            "load_geojson": tool_load_geojson,
            "load_kml": tool_load_kml,
            "load_csv": tool_load_csv,
            "fetch_geo_boundaries": tool_fetch_geo_boundaries,
        })

    def safe_json_loads(s: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(s or "{}")
        except Exception:
            return None

    def run_tool_call(tool_name: str, raw_args: Any) -> Optional[str]:
        if args.debug:
            print(f"[DEBUG] Requested tool: {tool_name} with args: {raw_args}")
        fn = tool_registry.get(tool_name)
        if not fn:
            print(f"[WARN] Unknown tool requested: {tool_name}")
            return None
        # raw_args may already be a dict; if string try to parse JSON
        if isinstance(raw_args, str):
            parsed = safe_json_loads(raw_args)
        elif isinstance(raw_args, dict):
            parsed = raw_args
        else:
            parsed = {}
        if parsed is None:
            print("[WARN] Could not parse tool arguments; using empty args.")
            parsed = {}
        try:
            return fn(parsed)
        except Exception as e:
            print(f"[ERROR] Tool '{tool_name}' failed: {e}")
            return None

    # Greet the user
    print("Hi, I'm Humboldt, your GeoAI Agent. How can I assist you today?")
    if args.debug:
        print("[DEBUG] Using model:", args.model)

    # REPL loop
    while True:
        user_input = input("Humboldt> (type 'exit' to quit)\n")
        if user_input.lower() in ("exit", "quit"):
            print("Exiting Humboldt. Goodbye!")
            break

        # Direct tool invocations
        if user_input.startswith("/geocode "):
            payload = user_input[len("/geocode "):]
            print(tool_geocode_locations({"locations": payload}))
            continue
        if user_input.startswith("/reverse "):
            payload = user_input[len("/reverse "):]
            print(tool_reverse_geocode_coordinates({"coordinates": payload}))
            continue
        if user_input.startswith("/dms "):
            payload = user_input[len("/dms "):]
            print(tool_convert_dd_to_dms({"coordinates": payload}))
            continue

        messages.append({"role": "user", "content": user_input})
        if args.debug:
            print("[DEBUG] Sending to LLM (last 2 msgs):", messages[-2:])

        # Multi-step tool loop
        steps = 0
        last_content_printed = False
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
            if args.debug:
                print("[DEBUG] LLM message:", message)

            if getattr(message, "function_call", None):
                call = message.function_call
                tool_output = run_tool_call(call.name, call.arguments)
                messages.append({"role": "assistant", "content": None, "function_call": call})
                messages.append({"role": "function", "name": call.name, "content": tool_output or ""})
                steps += 1
                continue

            if message.content:
                print(message.content)
                last_content_printed = True
                break

            break

        if steps > args.max_steps and not last_content_printed:
            print("[INFO] Reached maximum tool-call steps. Stopping.")

        if len(messages) > 20:
            messages = [messages[0]] + messages[-19:]


if __name__ == "__main__":
    main()
