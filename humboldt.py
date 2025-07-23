"""Run this model in Python

> pip install openai
"""

import json
import argparse
import os
import logging
from openai import OpenAI
from geocode import (
    geocode_locations,
    reverse_geocode_coordinates,
)  # import geocoding tools
from dd2dms import convert_dd_to_dms  # import DD→DMS conversion tool
from file_loaders import (
    load_geojson,
    load_kml,
    load_csv,
    fetch_geo_boundaries,
)


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
        default=os.getenv(
            "OPENAI_MODEL", "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
        ),
        help="LLM model name",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("HUMBOLDT_DEBUG", "0") in ("1", "true", "True"),
        help="Enable debug logging",
    )
    args = parser.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # System prompt describing the agent's role
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

    # Initialize chat history and tool schema once
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
    ]

    # Greet the user
    print("Hi, I'm Humboldt, your GeoAI Agent. How can I assist you today?")
    # REPL loop
    while True:
        user_input = input("Humboldt> (type 'exit' to quit)\n")
        if user_input.lower() in ("exit", "quit"):
            print("Exiting Humboldt. Goodbye!")
            break

        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        logging.debug("Sending to LLM: %s", messages)

        # First call (possibly function)
        response = client.chat.completions.create(
            model=args.model,
            messages=messages,
            functions=functions,
            function_call="auto",
            max_tokens=1000,
            frequency_penalty=1,
        )
        message = response.choices[0].message
        logging.debug("LLM response: %s", message)

        # If LLM requested our geocode tool
        if message.function_call:
            args = json.loads(message.function_call.arguments)
            # Status notifications for tool invocation
            if message.function_call.name == "geocode_locations":
                print("Status: Invoking geocoding agent...")
                table = geocode_locations(args["locations"])
            elif message.function_call.name == "convert_dd_to_dms":
                print("Status: Invoking DD to DMS conversion agent...")
                table = convert_dd_to_dms(args["coordinates"])
            elif message.function_call.name == "reverse_geocode_coordinates":
                print("Status: Invoking reverse geocoding agent...")
                table = reverse_geocode_coordinates(args["coordinates"])
            elif message.function_call.name == "load_geojson":
                print("Status: Loading GeoJSON data...")
                table = load_geojson(args["geojson"])
            elif message.function_call.name == "load_kml":
                print("Status: Loading KML data...")
                table = load_kml(args["kml"])
            elif message.function_call.name == "load_csv":
                print("Status: Loading CSV data...")
                table = load_csv(args["csv"])
            elif message.function_call.name == "fetch_geo_boundaries":
                print("Status: Downloading boundaries...")
                table = fetch_geo_boundaries(args["iso"], args.get("adm", "ADM0"))
            # Log tool output
            logging.debug("Tool output:\n%s", table)

            # Append the function call and its result to history
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": message.function_call,
                }
            )
            messages.append(
                {
                    "role": "function",
                    "name": message.function_call.name,
                    "content": table,
                }
            )

            # Second call to get the final assistant answer
            second_resp = client.chat.completions.create(
                model=args.model,
                messages=messages,
                max_tokens=1000,
                frequency_penalty=1,
            )
            print(second_resp.choices[0].message.content)

        else:
            # No tool call, just print the assistant reply
            print(message.content)


if __name__ == "__main__":
    main()
