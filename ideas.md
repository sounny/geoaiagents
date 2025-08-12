# Humboldt ideas and development status

A living list of improvements for a provider-agnostic GeoAI agent with a webchat-first UX. Each idea has a brief note and a status tag.

## Core scaffolding

- Provider-agnostic LLM adapter (LLMClient interface) with methods: chat, function_call, stream. Status: Partial (OpenAI client only; CLI flags for model/base-url exist)
- Support multiple providers via adapters: OpenAI-compatible, Hugging Face Inference API, local runtimes. Status: Planned
- Pluggable tool registry (easy to add/replace tools without touching agent loop). Status: Achieved (tool_registry pattern in humboldt.py)
- Multi-step tool loop with max-steps guard and safe JSON arg parsing. Status: Achieved
- Direct slash commands to call tools without the LLM (/geocode, /reverse, /dms). Status: Achieved
- Unified config via .env, CLI flags, and sensible defaults. Status: Partial (CLI flags present; .env supported via os.getenv)

## GIS tools and data I/O

- Geocoding tools (forward, reverse) with Nominatim (geopy). Status: Achieved
- DD → DMS converter for coordinate formatting. Status: Achieved
- File loader tools (GeoJSON, KML, CSV) to extract coordinates for mapping. Status: Partial (API scaffolding referenced; not yet in main)
- Geocoding provider abstraction (Nominatim, Mapbox, Google) behind a common interface. Status: Planned
- Result export helpers (CSV, GeoJSON) for downstream apps. Status: Planned
- Validation utilities for coordinates and feature collections. Status: Planned

## Webchat-first experience

- Webchat UI as primary interface; agent emits tool-call status and structured outputs. Status: Partial (present in other branch; not wired in this workspace)
- Map preview component (Leaflet) that reacts to geocode results and selection. Status: Planned
- Streaming responses in webchat (token-by-token + tool-call events). Status: Planned
- Upload support in webchat for GeoJSON/KML/CSV; pass file text to loader tools. Status: Planned

## Providers and runtimes

- Hugging Face integration (Inference API + Transformers local pipeline fallback). Status: Planned
- Local model backends (ONNX, llama.cpp) with a thin chat wrapper. Status: Planned
- Model selection and per-model capability flags (function-calling vs tool-calls). Status: Planned

## Reliability, performance, and ops

- Caching geocoding and reverse geocoding results (disk or sqlite) with TTL. Status: Planned
- Rate limiting and retry/backoff for Nominatim and provider APIs. Status: Planned
- Structured logging for tool calls and errors; debug flag surfaces internals. Status: Partial (debug logging and messages enabled)
- Telemetry hooks (simple event bus) to feed UI and logs concurrently. Status: Planned
- Robust error handling and user-facing recovery prompts. Status: Partial (safe arg parsing; needs richer guidance)

## Packaging and developer experience

- Auto dependency check/installation workflow with safe fallbacks. Status: Achieved
- Dockerfile + compose for “run anywhere” with local webchat. Status: Planned
- Unit/integration tests for tools and agent loop; CI on PRs. Status: Planned
- Minimal plugin API for registering new tools and schemas. Status: Planned
- Documentation for adapters (how to add a new provider/tool). Status: Planned

## Nice-to-haves

- RAG over geospatial docs (CRS guides, OSM tags) to augment answers. Status: Planned
- CRS transformers and datum conversions (pyproj integration). Status: Planned
- Batch geocoding with progress updates and resumable jobs. Status: Planned
- Offline mode for basic conversions and local models. Status: Planned

---

How to contribute: pick a Planned/Partial item, open an issue proposing the approach (adapter/tool/UX), then submit a PR with tests and docs. The agent loop is in `humboldt.py` and tools live beside it for now.
