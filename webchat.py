import json
import os
import logging
import re
from openai import OpenAI
import gradio as gr
import folium
from geocode import geocode_locations, reverse_geocode_coordinates
from dd2dms import convert_dd_to_dms
from file_loaders import (
    load_geojson,
    load_kml,
    load_csv,
    fetch_geo_boundaries,
)

# Initialize OpenAI client using environment variables or defaults
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:5272/v1/")
API_KEY = os.getenv("OPENAI_API_KEY", "unused")
MODEL_NAME = os.getenv(
    "OPENAI_MODEL", "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
)
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# Configure logging similarly to humboldt.py
DEBUG = os.getenv("HUMBOLDT_DEBUG", "0") in ("1", "true", "True")
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(levelname)s: %(message)s",
)

# Store log entries for display in the UI
log_history: list[str] = []


def infer_location(message: str) -> str | None:
    """Return a location string if message looks like a map request."""
    m = re.search(r"for ([A-Za-z0-9, ]+)", message, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def create_map_html(points: list[tuple[float, float]]) -> str:
    """Return HTML for a folium map with given points."""
    if not points:
        return ""
    m = folium.Map(location=points[0], zoom_start=4)
    for lat, lon in points:
        folium.Marker([lat, lon]).add_to(m)
    return m._repr_html_()


# Last rendered map HTML so the map persists when no new data is returned
LAST_MAP_HTML = create_map_html([(0.0, 0.0)])


def parse_table_coordinates(
    table: str, lat_index: int, lon_index: int
) -> list[tuple[float, float]]:
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
    "of Alexander von Humboldt, the father of Modern Geography. You must "
    "always use the provided function tools to perform geospatial tasks and "
    "never guess results. When you invoke a tool it will be logged for the "
    "user to see. If the user requests a map marker or location to be shown, "
    "call `geocode_locations` first so the interface can display the point. "
    "Do not claim you are unable to manipulate maps or geospatial data; use "
    "the provided tools and let the interface handle map updates."
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
        model=MODEL_NAME,
        messages=messages,
        functions=functions,
        function_call="auto",
        max_tokens=1000,
        frequency_penalty=1,
    )
    msg = response.choices[0].message
    logging.debug("LLM response: %s", msg)
    global LAST_MAP_HTML
    map_html = ""
    table = ""
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
        elif msg.function_call.name == "fetch_geo_boundaries":
            logging.info("Invoking fetch_geo_boundaries...")
            table = fetch_geo_boundaries(args["iso"], args.get("adm", "ADM0"))
            coords = parse_table_coordinates(table, 0, 1)
            map_html = create_map_html(coords)
        else:
            table = ""
        messages.append(
            {"role": "assistant", "content": None, "function_call": msg.function_call}
        )
        messages.append(
            {"role": "function", "name": msg.function_call.name, "content": table}
        )
        second = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=1000,
            frequency_penalty=1,
        )
        reply = second.choices[0].message.content
        logging.info("LLM response received")
    else:
        reply = msg.content
        logging.info("LLM response received")
        location = infer_location(message)
        if location:
            logging.info("Auto geocoding: %s", location)
            table = geocode_locations(location)
            coords = parse_table_coordinates(table, 2, 3)
            map_html = create_map_html(coords)
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": "geocode_locations",
                        "arguments": json.dumps({"locations": location}),
                    },
                }
            )
            messages.append(
                {"role": "function", "name": "geocode_locations", "content": table}
            )
            second = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=1000,
                frequency_penalty=1,
            )
            reply = second.choices[0].message.content
    if map_html:
        LAST_MAP_HTML = map_html
    else:
        map_html = LAST_MAP_HTML
    messages.append({"role": "assistant", "content": reply})
    return reply, map_html, "\n".join(log_history), table


def chat(message, history, upload_file):
    """Wrapper for respond() that formats history for gr.Chatbot."""
    reply, map_html, logs, table = respond(message, history, upload_file)
    # Format history for gr.Chatbot with type="messages"
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply},
    ]
    return history, map_html, logs, table


def main():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=3):
                map_box = gr.HTML(LAST_MAP_HTML, label="Map")
                chatbot = gr.Chatbot(type="messages")
                message = gr.Textbox(label="Message")
                send_btn = gr.Button("Send")
            with gr.Column(scale=1):
                with gr.Accordion("Upload & Logs", open=False):
                    upload = gr.File(
                        label="Upload Data",
                        file_types=[".geojson", ".json", ".kml", ".csv"],
                    )
                    log_box = gr.Textbox(label="Logs", lines=10, interactive=False)
                    data_box = gr.Textbox(
                        label="Data Table", lines=10, interactive=False
                    )

        send_btn.click(
            chat,
            inputs=[message, chatbot, upload],
            outputs=[chatbot, map_box, log_box, data_box],
        )
        message.submit(
            chat,
            inputs=[message, chatbot, upload],
            outputs=[chatbot, map_box, log_box, data_box],
        )
    demo.launch()


if __name__ == "__main__":
    main()
