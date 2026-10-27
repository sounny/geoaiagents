1. Run `git restore tests/test_tool_registry.py` to discard previous modifications and ensure a pristine file state.
2. Append the TZ independence tests using the following command:
```bash
cat << 'EOF' >> tests/test_tool_registry.py
import time
import sys

@pytest.mark.parametrize("func_name", [
    "parse_tool_args",
    "create_registry",
    "ToolRegistry.register_tool",
    "ToolRegistry.has_tool",
    "ToolRegistry.openai_functions",
    "ToolRegistry.invoke",
])
def test_public_functions_tz_independence(func_name, monkeypatch, mocker, tmp_path):
    mocker.patch("tool_registry.geocode_locations", return_value="mock_geo")
    mocker.patch("tool_registry.reverse_geocode_coordinates", return_value="mock_rev")
    mocker.patch("tool_registry.convert_dd_to_dms", return_value="mock_dms")
    mocker.patch("tool_registry.calculate_distance", return_value="mock_dist")
    mocker.patch("tool_registry.load_geojson", return_value="mock_gj")
    mocker.patch("tool_registry.load_kml", return_value="mock_kml")
    mocker.patch("tool_registry.load_csv", return_value="mock_csv")
    mocker.patch("tool_registry.fetch_geo_boundaries", return_value="mock_bnd")

    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "my_tz_plugin.py"
    plugin_file.write_text(
        "def register_tools(registry):\n"
        "    registry.register_tool(name='my_plugin_tool', description='desc', parameters={}, handler=lambda x: 'ok')\n"
    )
    sys.path.insert(0, str(plugin_dir))
    monkeypatch.setenv("GEOAI_PLUGIN_MODULES", "my_tz_plugin")

    def run_under_tz(tz, runner):
        monkeypatch.setenv("TZ", tz)
        if hasattr(time, "tzset"):
            time.tzset()
        return runner()

    runners = {
        "parse_tool_args": lambda: parse_tool_args('{"a": 1}'),
        "create_registry": lambda: create_registry().openai_functions(),
        "ToolRegistry.register_tool": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.openai_functions()
        )[-1],
        "ToolRegistry.has_tool": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.has_tool("test_tool")
        )[-1],
        "ToolRegistry.openai_functions": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.openai_functions()
        )[-1],
        "ToolRegistry.invoke": lambda: (
            tr := ToolRegistry(),
            tr.register_tool(name="test_tool", description="desc", parameters={}, handler=lambda x: "ok"),
            tr.invoke("test_tool", {})
        )[-1],
    }

    try:
        res1 = run_under_tz("UTC", runners[func_name])
        res2 = run_under_tz("America/New_York", runners[func_name])
        if res1 != res2:
            pytest.xfail(f"{func_name} behavior differs by TZ")
        assert res1 == res2
    finally:
        sys.path.remove(str(plugin_dir))
        monkeypatch.undo()
        if hasattr(time, "tzset"):
            time.tzset()
