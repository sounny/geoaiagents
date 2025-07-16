# geocode.py: LLM-driven geocoder using OpenAI function-calling and geopy Nominatim API
"""Run this model in Python

> pip install geopy
"""
# Standard library imports
import json  # to parse and format JSON for function arguments
import argparse
import os
# Third-party imports
from openai import OpenAI  # OpenAI client for LLM interaction
from geopy.geocoders import Nominatim  # Nominatim geocoder for OpenStreetMap
from geopy.exc import GeocoderTimedOut, GeocoderServiceError  # handle geocoding errors

# Geocoding helper functions

def get_coordinates(location_query):
    """
    Query Nominatim API for a single location string.
    Returns a tuple (matched address, latitude, longitude) or (None, None, None) if not found.
    """
    geolocator = Nominatim(user_agent="my_geocoder_app")
    try:
        location = geolocator.geocode(location_query)
        if location:
            return location.address, location.latitude, location.longitude
        else:
            return None, None, None
    except (GeocoderTimedOut, GeocoderServiceError, Exception):
        # Return empty tuple on any geocoding failure
        return None, None, None


def parse_locations(locations_str):
    """
    Split a string of locations (newline or semicolon delimited) into a list.
    """
    import re
    return [line.strip() for line in re.split(r'\n|;', locations_str) if line.strip()]


def geocode_locations(locations_str: str) -> str:
    """
    Geocode multiple locations and return a markdown-formatted table.
    """
    locations = parse_locations(locations_str)
    rows = []
    for loc in locations:
        address, lat, lon = get_coordinates(loc)
        # Use placeholders on missing data
        address = address or "Not found"
        lat = lat or ""
        lon = lon or ""
        rows.append((loc, address, lat, lon))
    # Build markdown table header
    table = [
        "| Input | Matched Address | Latitude | Longitude |",
        "|-------|-----------------|----------|-----------|"
    ]
    # Append each row
    for inp, addr, lat, lon in rows:
        table.append(f"| {inp} | {addr} | {lat} | {lon} |")
    # Join lines and return
    return "\n".join(table)


def main():
    """
    Main program flow:
      1. Initialize LLM client
      2. Read user locations
      3. Send prompt to LLM with function schema
      4. Execute function calls or fallback locally
      5. Display results and datum
    """
    parser = argparse.ArgumentParser(description="LLM-driven geocoder")
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
    args = parser.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    # Prompt the user for location input
    user_input = input(
        "Hello! I am a Geocoding Agent. Give me your locations and I will provide you with Longitude and Latitude Coordinates. Separate multiple locations with a semicolon.\n"
    )

    # System prompt defines agent behavior
    system_prompt = (
        "You are a geocoder. The user will give you addresses, places, "
        "and locations. Your job is to convert them to longitude and latitude, "
        "and provide a table with the original input and coordinates."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    # Define function schema for LLM to call geocode_locations
    functions = [
        {
            "name": "geocode_locations",
            "description": "Geocode a list of locations and return a markdown table",
            "parameters": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited list of locations."
                    }
                },
                "required": ["locations"]
            }
        }
    ]

    # First interaction with the LLM
    response = client.chat.completions.create(
        model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
        messages=messages,
        functions=functions,
        function_call="auto",
        max_tokens=1000,
        frequency_penalty=1,
    )
    message = response.choices[0].message

    # If LLM requests our function, execute and return results
    if message.function_call:
        args = json.loads(message.function_call.arguments)
        table = geocode_locations(args["locations"])
        # Append the function call and its result
        messages.append({"role": "assistant", "content": None, "function_call": message.function_call})
        messages.append({"role": "function", "name": message.function_call.name, "content": table})
        # Send back to LLM for final formatting
        second_resp = client.chat.completions.create(
            model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
            messages=messages,
            max_tokens=1000,
            frequency_penalty=1,
        )
        print(second_resp.choices[0].message.content)
        # Indicate datum and format
        print("\nDatum: WGS84 (coordinates shown in Decimal Degrees).")
    else:
        # Fallback: local geocoding if LLM did not call function
        table = geocode_locations(user_input)
        print(table)
        print("\nDatum: WGS84 (coordinates shown in Decimal Degrees).")


if __name__ == "__main__":
    main()
