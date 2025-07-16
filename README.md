# geoaiagents
AI agents for GIS and Remote Sensing workflows.

## Requirements

- Python 3.8 or higher
- geopy >=2.0
- openai >=1.0

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

Command line flags `--base-url` and `--api-key` override the environment
variables.

Example using environment variables:

```bash
export OPENAI_BASE_URL=http://localhost:5272/v1/
export OPENAI_API_KEY=my-key
python geocode.py
```

Or overriding on the command line:

```bash
python humboldt.py --base-url https://api.example.com/v1 --api-key sk-...
```

## Scripts

### geocode.py

This script uses the `geopy` library to geocode locations via OpenStreetMap's Nominatim API.
It also demonstrates OpenAI function-calling by returning results in a markdown table.

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

## Extending with New Tools

Future agents and tools can be added by defining function schemas in `humboldt.py` and implementing the corresponding Python functions.

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
