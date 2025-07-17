"""Run this model in Python

> pip install openai
"""
import json
import argparse
import os
from openai import OpenAI
from geocode import geocode_locations, reverse_geocode_coordinates  # import geocoding tools
from dd2dms import convert_dd_to_dms  # import DD→DMS conversion tool

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
    args = parser.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    # System prompt describing the agent's role
    system_prompt = (
        "You are a GeoAI Agent who is an expert GIS and Remote Sensing Analyst, "
        "cartographer, and Geospatial Developer. Your name is Humboldt, in honor "
        "of Alexander von Humboldt, the father of Modern Geography. You will "
        "take user needs, call upon specialized tools (like geocoding), and "
        "manage their inputs and outputs to fulfill the request."
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
                        "description": "Newline- or semicolon-delimited list of locations to geocode"
                    }
                },
                "required": ["locations"]
            }
        },
        {
            "name": "convert_dd_to_dms",
            "description": "Convert decimal-degree coordinates to DMS table",
            "parameters": {
                "type": "object",
                "properties": {
                    "coordinates": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited DD lat,lon pairs"
                    }
                },
                "required": ["coordinates"]
            }
        },
        {
            "name": "reverse_geocode_coordinates",
            "description": "Reverse geocode lat/lon pairs to addresses",
            "parameters": {
                "type": "object",
                "properties": {
                    "coordinates": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited DD lat,lon pairs"
                    }
                },
                "required": ["coordinates"]
            }
        }
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
        print("[DEBUG] Sending to LLM:", messages)

        # First call (possibly function)
        response = client.chat.completions.create(
            model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
            messages=messages,
            functions=functions,
            function_call="auto",
            max_tokens=1000,
            frequency_penalty=1,
        )
        message = response.choices[0].message
        print("[DEBUG] LLM response:", message)

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
            # Log tool output
            print("[DEBUG] Tool output:\n", table)

            # Append the function call and its result to history
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": message.function_call
            })
            messages.append({
                "role": "function",
                "name": message.function_call.name,
                "content": table
            })

            # Second call to get the final assistant answer
            second_resp = client.chat.completions.create(
                model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
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