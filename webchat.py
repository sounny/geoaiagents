import json
import os
from openai import OpenAI
import gradio as gr
from geocode import geocode_locations, reverse_geocode_coordinates
from dd2dms import convert_dd_to_dms

# Initialize OpenAI client using environment variables or defaults
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:5272/v1/")
API_KEY = os.getenv("OPENAI_API_KEY", "unused")
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# System prompt mirrors the one in humboldt.py
system_prompt = (
    "You are a GeoAI Agent who is an expert GIS and Remote Sensing Analyst, "
    "cartographer, and Geospatial Developer. Your name is Humboldt, in honor "
    "of Alexander von Humboldt, the father of Modern Geography. You will "
    "take user needs, call upon specialized tools (like geocoding), and "
    "manage their inputs and outputs to fulfill the request."
)

# Conversation state shared across requests
messages = [{"role": "system", "content": system_prompt}]

# Function schema for tool calls
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

def respond(message: str, history: list[tuple[str, str]]):
    """Handle a chat message and return the agent's reply."""
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
        messages=messages,
        functions=functions,
        function_call="auto",
        max_tokens=1000,
        frequency_penalty=1,
    )
    msg = response.choices[0].message
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        if msg.function_call.name == "geocode_locations":
            table = geocode_locations(args["locations"])
        elif msg.function_call.name == "convert_dd_to_dms":
            table = convert_dd_to_dms(args["coordinates"])
        elif msg.function_call.name == "reverse_geocode_coordinates":
            table = reverse_geocode_coordinates(args["coordinates"])
        else:
            table = ""
        messages.append({"role": "assistant", "content": None, "function_call": msg.function_call})
        messages.append({"role": "function", "name": msg.function_call.name, "content": table})
        second = client.chat.completions.create(
            model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
            messages=messages,
            max_tokens=1000,
            frequency_penalty=1,
        )
        reply = second.choices[0].message.content
    else:
        reply = msg.content
    messages.append({"role": "assistant", "content": reply})
    return reply


def main():
    iface = gr.ChatInterface(respond, title="Humboldt GeoAI Agent")
    iface.launch()


if __name__ == "__main__":
    main()
