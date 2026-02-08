"""Example plugin module for GeoAI tool registration.

Enable by setting:
    export GEOAI_PLUGIN_MODULES=plugins.example_plugin
"""


def register_tools(registry):
    """Register example tools with the shared registry."""

    def ping_api(arguments):
        endpoint = arguments.get("endpoint", "unknown")
        return (
            "| endpoint | status |\n"
            "|---|---|\n"
            f"| {endpoint} | plugin-ok |"
        )

    registry.register_tool(
        name="ping_api",
        description="Example plugin tool to demonstrate external API integration",
        parameters={
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint name or URL to test",
                }
            },
            "required": ["endpoint"],
        },
        handler=ping_api,
    )
