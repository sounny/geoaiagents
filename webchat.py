import json
import os
import logging
from openai import OpenAI
import gradio as gr
import folium
from geocode import geocode_locations, reverse_geocode_coordinates
from dd2dms import convert_dd_to_dms
from file_loaders import load_geojson, load_kml, load_csv

# Initialize OpenAI client using environment variables or defaults
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:5272/v1/")
API_KEY = os.getenv("OPENAI_API_KEY", "unused")
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Configure logging similarly to humboldt.py
DEBUG = os.getenv("HUMBOLDT_DEBUG", "0") in ("1", "true", "True")
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(levelname)s: %(message)s",
)

# Store log entries for display in the UI
log_history: list[str] = []


def create_map_html(points: list[tuple[float, float]]) -> str:
    """Return HTML for a folium map with given points."""
    if not points:
        return ""
    m = folium.Map(location=points[0], zoom_start=4)
    for lat, lon in points:
        folium.Marker([lat, lon]).add_to(m)
    return m._repr_html_()


def parse_table_coordinates(table: str, lat_index: int, lon_index: int) -> list[tuple[float, float]]:
    """Parse coordinate pairs from a markdown table."""
    coords: list[tuple[float, float]] = []
    lines = table.splitlines()[2:]
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) <= max(lat_index, lon_index):
            continue
        try:
            lat = float(cells[lat_index])
            lon = float(cells[lon_index])
        except ValueError:
            continue
        coords.append((lat, lon))
    return coords


class GradioLogHandler(logging.Handler):
    """Logging handler that appends formatted records to log_history."""

    def emit(self, record: logging.LogRecord) -> None:
        log_history.append(self.format(record))


logging.getLogger().addHandler(GradioLogHandler())

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
        "description": "Load GeoJSON text and return a coordinate table",
        "parameters": {
            "type": "object",
            "properties": {"geojson": {"type": "string", "description": "Contents of a GeoJSON file"}},
            "required": ["geojson"]
        }
    },
    {
        "name": "load_kml",
        "description": "Load KML text and return a coordinate table",
        "parameters": {
            "type": "object",
            "properties": {"kml": {"type": "string", "description": "Contents of a KML file"}},
            "required": ["kml"]
        }
    },
    {
        "name": "load_csv",
        "description": "Load CSV text with latitude/longitude columns",
        "parameters": {
            "type": "object",
            "properties": {"csv": {"type": "string", "description": "Contents of a CSV file"}},
            "required": ["csv"]
        }
    }
]

def respond(message: str, history: list[dict], upload_file=None):
    """Handle a chat message and return the agent's reply."""
    if upload_file is not None:
        try:
            with open(upload_file.name, "r", encoding="utf-8", errors="ignore") as f:
                file_text = f.read(10000)
            message = f"{message}\n\nUploaded file `{os.path.basename(upload_file.name)}`:\n{file_text}"
        except Exception:
            pass
    messages.append({"role": "user", "content": message})
    logging.debug("Sending to LLM: %s", messages)
    response = client.chat.completions.create(
        model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
        messages=messages,
        functions=functions,
        function_call="auto",
        max_tokens=1000,
        frequency_penalty=1,
    )
    msg = response.choices[0].message
    logging.debug("LLM response: %s", msg)
    map_html = ""
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        if msg.function_call.name == "geocode_locations":
            logging.info("Invoking geocode_locations...")
            table = geocode_locations(args["locations"])
            coords = parse_table_coordinates(table, 2, 3)
            map_html = create_map_html(coords)
        elif msg.function_call.name == "convert_dd_to_dms":
            logging.info("Invoking convert_dd_to_dms...")
            table = convert_dd_to_dms(args["coordinates"])
            coords = parse_table_coordinates(table, 0, 1)
            map_html = create_map_html(coords)
        elif msg.function_call.name == "reverse_geocode_coordinates":
            logging.info("Invoking reverse_geocode_coordinates...")
            table = reverse_geocode_coordinates(args["coordinates"])
            coords = parse_table_coordinates(table, 0, 1)
            map_html = create_map_html(coords)
        elif msg.function_call.name == "load_geojson":
            logging.info("Invoking load_geojson...")
            table = load_geojson(args["geojson"])
            coords = parse_table_coordinates(table, 0, 1)
            map_html = create_map_html(coords)
        elif msg.function_call.name == "load_kml":
            logging.info("Invoking load_kml...")
            table = load_kml(args["kml"])
            coords = parse_table_coordinates(table, 0, 1)
            map_html = create_map_html(coords)
        elif msg.function_call.name == "load_csv":
            logging.info("Invoking load_csv...")
            table = load_csv(args["csv"])
            coords = parse_table_coordinates(table, 0, 1)
            map_html = create_map_html(coords)
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
        logging.info("LLM response received")
    else:
        reply = msg.content
        logging.info("LLM response received")
    messages.append({"role": "assistant", "content": reply})
    return reply, map_html, "\n".join(log_history)


def main():
    with gr.Blocks() as demo:
        upload = gr.File(label="Upload Data", file_types=[".geojson", ".json", ".kml", ".csv"])
        map_box = gr.HTML(label="Map")
        log_box = gr.Textbox(label="Logs", lines=10, interactive=False)
        gr.ChatInterface(
            respond,
            title="Humboldt GeoAI Agent",
            additional_inputs=[upload],
            additional_outputs=[map_box, log_box],
            chatbot=gr.Chatbot(type="messages"),
        )
    demo.launch()


if __name__ == "__main__":
    main()
