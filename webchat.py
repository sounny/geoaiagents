import json
import os
from openai import OpenAI
import gradio as gr
import folium
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

# --- Map helpers -----------------------------------------------------------
def _extract_coords(table: str):
    """Parse markdown table rows and return list of (lat, lon, label)."""
    coords = []
    lines = table.splitlines()[2:]  # skip header
    for line in lines:
        parts = [p.strip() for p in line.strip().strip('|').split('|')]
        if len(parts) >= 4:
            try:
                lat = float(parts[2])
                lon = float(parts[3])
            except Exception:
                continue
            label = parts[0]
            coords.append((lat, lon, label))
    return coords


def _render_map(markers):
    """Return HTML for a folium map with markers."""
    if markers:
        avg_lat = sum(m[0] for m in markers) / len(markers)
        avg_lon = sum(m[1] for m in markers) / len(markers)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)
    else:
        m = folium.Map(location=[0, 0], zoom_start=2)
    for lat, lon, label in markers:
        folium.Marker([lat, lon], popup=label).add_to(m)
    return m._repr_html_()

def respond(message: str, history: list[tuple[str, str]], markers: list):
    """Handle a chat message, update map markers and return reply."""
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
    new_markers = []
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        if msg.function_call.name == "geocode_locations":
            table = geocode_locations(args["locations"])
            new_markers = _extract_coords(table)
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
    history.append((message, reply))
    markers.extend(new_markers)
    map_html = _render_map(markers)
    return history, map_html, markers


def main():
    with gr.Blocks() as demo:
        gr.Markdown("# Humboldt GeoAI Agent")
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot()
                msg = gr.Textbox(placeholder="Enter a message and press Enter")
            with gr.Column():
                map_html = gr.HTML()
        markers = gr.State([])

        msg.submit(respond, [msg, chatbot, markers], [chatbot, map_html, markers])
        msg.submit(lambda: "", None, msg)

    demo.launch()


if __name__ == "__main__":
    main()
