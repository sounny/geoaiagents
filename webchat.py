import json
import os
from openai import OpenAI
import gradio as gr
import folium
from geocode import geocode_locations, reverse_geocode_coordinates
from dd2dms import convert_dd_to_dms
from parsers import load_geojson, load_kml, load_csv

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
    },
    {
        "name": "load_geojson",
        "description": "Load a GeoJSON file and return its contents",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the GeoJSON file"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "load_kml",
        "description": "Load a KML file and return it as GeoJSON",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the KML file"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "load_csv",
        "description": "Load a CSV with lat/lon columns as GeoJSON",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the CSV file"
                }
            },
            "required": ["path"]
        }
    }
]

def geojson_map_html(data):
    """Render GeoJSON data on a Leaflet map returned as HTML."""
    m = folium.Map(location=[0, 0], zoom_start=2)
    if data and data.get("features"):
        lats, lons = [], []
        for f in data["features"]:
            geom = f.get("geometry", {})
            if geom.get("type") == "Point":
                lon, lat = geom.get("coordinates", [0, 0])
                folium.Marker([lat, lon], tooltip=f.get("properties", {}).get("name", "")).add_to(m)
                lats.append(lat); lons.append(lon)
            else:
                folium.GeoJson(f).add_to(m)
        if lats and lons:
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    return m._repr_html_()


def respond(message: str, history: list[tuple[str, str]], file, geojson_state):
    """Handle a chat message with optional file upload."""
    if file is not None:
        ext = os.path.splitext(file.name).lower()
        if ext.endswith(".geojson") or ext.endswith(".json"):
            geojson_state = load_geojson(file.name)
        elif ext.endswith(".kml"):
            geojson_state = load_kml(file.name)
        elif ext.endswith(".csv"):
            geojson_state = load_csv(file.name)

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
        elif msg.function_call.name == "load_geojson":
            geojson_state = load_geojson(args["path"])
            table = f"Loaded {len(geojson_state.get('features', []))} features"
        elif msg.function_call.name == "load_kml":
            geojson_state = load_kml(args["path"])
            table = f"Loaded {len(geojson_state.get('features', []))} features"
        elif msg.function_call.name == "load_csv":
            geojson_state = load_csv(args["path"])
            table = f"Loaded {len(geojson_state.get('features', []))} features"
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
    map_html = geojson_map_html(geojson_state) if geojson_state else ""
    return reply, geojson_state, map_html


def main():
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(type="messages")
        msg = gr.Textbox()
        file_input = gr.File(label="Upload data")
        map_output = gr.HTML()
        state = gr.State(None)

        def submit(user_message, file, chat_history, geojson_state):
            reply, geojson_state, map_html = respond(user_message, chat_history, file, geojson_state)
            chat_history = chat_history + [(user_message, reply)]
            return "", chat_history, geojson_state, map_html

        msg.submit(
            submit,
            inputs=[msg, file_input, chatbot, state],
            outputs=[msg, chatbot, state, map_output],
        )
        demo.launch()


if __name__ == "__main__":
    main()
