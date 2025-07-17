"""Run this model in Python

> pip install openai
"""
import json
import argparse
import os
from openai import OpenAI

"""
Convert Decimal Degrees (DD) to Degrees-Minutes-Seconds (DMS) via Python math,
using OpenAI function-calling to pass data through the LLM.
"""

# Conversion helper functions
def dd_to_dms_value(dd: float):
    """Convert a decimal degree value to DMS components with float seconds using total seconds."""
    sign = -1 if dd < 0 else 1
    abs_dd = abs(dd)
    # Total seconds from decimal degrees
    total_seconds = abs_dd * 3600.0
    # Degrees
    deg = int(total_seconds // 3600)
    # Remaining seconds after degrees
    rem = total_seconds - deg * 3600
    # Minutes
    minutes = int(rem // 60)
    # Remaining seconds after minutes
    seconds = rem - minutes * 60

    # Handle roll-over at seconds >= 59.9995 → increment minute
    if seconds >= 59.9995:
        seconds = 0.0
        minutes += 1
    # Handle roll-over at minutes == 60 → increment degree
    if minutes == 60:
        minutes = 0
        deg += 1

    return deg * sign, minutes, seconds

def format_dms(deg: int, minutes: int, seconds: float, is_lat: bool):
    """Format DMS components into a string with two decimal places for seconds."""
    if is_lat:
        direction = 'N' if deg >= 0 else 'S'
    else:
        direction = 'E' if deg >= 0 else 'W'
    return f"{abs(deg)}°{minutes:02d}'{seconds:05.2f}\" {direction}"

def convert_dd_to_dms(coordinates_str: str) -> str:
    """
    Convert newline- or semicolon-delimited DD lat,lon pairs to a markdown table of DMS.
    """
    import re
    lines = [line.strip() for line in re.split(r'\n|;', coordinates_str) if line.strip()]
    rows = []
    for line in lines:
        parts = re.split(r'[,\s]+', line)
        try:
            lat_dd = float(parts[0]); lon_dd = float(parts[1])
        except:
            continue
        lat_d, lat_m, lat_s = dd_to_dms_value(lat_dd)
        lon_d, lon_m, lon_s = dd_to_dms_value(lon_dd)
        lat_dms = format_dms(lat_d, lat_m, lat_s, True)
        lon_dms = format_dms(lon_d, lon_m, lon_s, False)
        rows.append((lat_dd, lon_dd, lat_dms, lon_dms))
    # Build markdown table
    table = [
        "| Latitude (DD) | Longitude (DD) | Latitude (DMS) | Longitude (DMS) |",
        "|--------------:|---------------:|---------------|---------------|"
    ]
    for lat_dd, lon_dd, lat_dms, lon_dms in rows:
        table.append(f"| {lat_dd:14.6f} | {lon_dd:15.6f} | {lat_dms:13} | {lon_dms:13} |")
    return "\n".join(table)

def main():
    parser = argparse.ArgumentParser(description="DD to DMS converter")
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

    # Initialize OpenAI client
    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    # Read user input
    user_input = input("Enter decimal-degree coordinates (newline or semicolon separated):\n")

    # System prompt
    system_prompt = (
        "You are a coordinate converter. The user provides decimal-degree latitude and longitude. "
        "Your job is to call the function to convert them to DMS and return a markdown table."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    # Function schema for LLM
    functions = [
        {
            "name": "convert_dd_to_dms",
            "description": "Convert decimal-degree coordinates to DMS table",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "string"}},
                "required": ["coordinates"]
            }
        }
    ]

    # LLM call
    response = client.chat.completions.create(
        model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
        messages=messages,
        functions=functions,
        function_call={"name": "convert_dd_to_dms"},  # force function call
        max_tokens=1000,
        frequency_penalty=1,
    )
    message = response.choices[0].message

    # Execute function if called
    if message.function_call:
        args = json.loads(message.function_call.arguments)
        table = convert_dd_to_dms(args["coordinates"])
        # >>> instead of going back to the LLM for a second_resp, just print it:
        print(table)
    else:
        # Fallback: direct output
        print(message.content)

if __name__ == "__main__":
    main()
