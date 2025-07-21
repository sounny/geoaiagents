# geoaiagents
AI agents for GIS and Remote Sensing workflows.

## Requirements

- Python 3.8 or higher
- geopy >=2.0
- openai >=1.0
- requests >=2.0

Install the dependencies with:
```bash
pip install -r requirements.txt
```

## Configuration

The scripts use the OpenAI client, which defaults to a local test server. You
can configure the API endpoint and key using environment variables or command
line flags.

- `OPENAI_BASE_URL` – base URL of the API (default `http://localhost:5272/v1/`)
- `OPENAI_API_KEY` – API key (default `unused`)
- `HUMBOLDT_DEBUG` – set to `1` to enable debug logging
- `OPENAI_MODEL` – LLM model name used by Humboldt and the web chat

Command line flags `--base-url`, `--api-key` and `--debug` override the environment
variables.

Example using environment variables:

```bash
export OPENAI_BASE_URL=http://localhost:5272/v1/
export OPENAI_API_KEY=my-key
export OPENAI_MODEL=Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx
python geocode.py
```

Or overriding on the command line:

```bash
python humboldt.py --base-url https://api.example.com/v1 --api-key sk-... \
    --model Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx
```
Add `--debug` (or set `HUMBOLDT_DEBUG=1`) to enable debug output.

## Scripts

### geocode.py

This script uses the `geopy` library to geocode locations via OpenStreetMap's Nominatim API.
It also demonstrates OpenAI function-calling by returning results in a markdown table.

The helper functions `get_coordinates` and `reverse_geocode_coordinates` now
accept optional parameters for the Nominatim requests. You can tweak the
`timeout` (default `1` second), specify a `bounding_box` in the form
`(west, south, east, north)` to confine results, and set the response
`language` (default `"en"`).

**Usage:**
```bash
python geocode.py
```
You will be prompted to enter locations (semicolon-separated). The script outputs a table of inputs and their coordinates (WGS84, Decimal Degrees).

### humboldt.py

Humboldt is an interactive REPL agent built on an LLM. It keeps conversation context and can call specialized tools (like geocoding) to fulfill user requests.

**Usage:**
```bash
python humboldt.py
```
At the prompt, enter commands such as:
```
Humboldt> Geocode Austin, TX; Paris, France
```
Humboldt will call the geocode tool and return a formatted table.

You can also ask Humboldt to convert coordinates into an address:
```
Humboldt> Reverse geocode 40.6892,-74.0445
```
Humboldt will look up the nearest location and print the address.

### Fetching Political Boundaries

Humboldt can retrieve simplified boundary data from the
[geoBoundaries](https://www.geoboundaries.org) API. Use the
`fetch_geo_boundaries` tool with an ISO country code to download GeoJSON
boundaries and display them on the map.

### webchat.py

`webchat.py` launches a simple Gradio interface that exposes Humboldt in your
browser. It reuses the same tools as the REPL but provides a chat box for
interaction.

**Usage:**
```bash
python webchat.py
```
Gradio will print a local URL that you can open in your browser. A small `manifest.json` is included to avoid 404 errors in the console.

## Extending with New Tools

Future agents and tools can be added by defining function schemas in `humboldt.py` and implementing the corresponding Python functions.

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
