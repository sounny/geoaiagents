# GeoAI Agents - Development Notes

## Project Overview

GeoAI Agents is a collection of AI-powered tools for GIS and Remote Sensing workflows. The main components are:

- **Humboldt**: Interactive terminal-based agent that orchestrates specialized tools
- **Geocoding Agent**: Converts addresses/places to lat/long coordinates using Nominatim API
- **DD2DMS Converter**: Converts decimal degrees to degrees-minutes-seconds format
- **Web Interface**: Browser-based chat interface with map visualization
- **File Loaders**: Tools for processing GeoJSON, KML, and CSV spatial data

## Architecture

The system uses OpenAI function-calling to let LLMs invoke Python tools. Each tool performs specific geospatial operations and returns structured data (typically markdown tables). The agents maintain conversation context and can chain multiple tool calls.

## Instructions for Future AI Development Agents

**IMPORTANT**: When you work on this project, please add brief notes below in the "Agent Development Log" section. This helps future agents understand:

- What changes you made and why
- Technical decisions and trade-offs
- Known issues or limitations
- Suggestions for improvements

Keep entries concise but informative. Include the date and a brief description of your contribution.

## Agent Development Log

### 2025-07-19 - Initial Project Setup
- Created core geocoding and DD2DMS conversion tools
- Implemented Humboldt terminal agent with function-calling
- Added web interface with Gradio and map visualization
- Set up environment variables and requirements management
- **Technical Notes**: Used geopy/Nominatim for geocoding, folium for maps
- **Issues**: LLM sometimes generates text instead of calling functions - fixed with explicit system prompts

### 2025-07-19 - Enhanced Web Interface
- Added file upload support for GeoJSON, KML, CSV
- Integrated interactive maps using folium
- Added logging system for debugging
- **Technical Notes**: Map coordinates extracted from table parsing, markers auto-generated
- **Limitations**: Limited to 10KB file uploads, basic coordinate extraction

---

## Guidelines for Future Development

1. **Tool Design**: Each tool should be self-contained with clear input/output formats
2. **Function Schemas**: Keep parameter descriptions specific to help LLM understand usage
3. **Error Handling**: Add robust error handling for network timeouts and malformed data
4. **Testing**: Test tools individually before integrating with agents
5. **Documentation**: Update README.md when adding new capabilities

## Known Technical Debt

- Conversation state in webchat.py is global (not session-isolated)
- Limited file format support for uploads
- No authentication or rate limiting on web interface
- Hardcoded model name throughout codebase

## Future Enhancement Ideas

- Add support for more coordinate systems (UTM, State Plane)
- Implement spatial analysis tools (distance, area calculations)
- Add raster data processing capabilities
- Create batch processing workflows
- Add user authentication and session management
