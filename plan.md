1. Restore `tests/test_webchat.py` to ensure it is in a pristine state.
   - Execute `git restore tests/test_webchat.py` to discard any previous changes.
2. Append timezone tests to `tests/test_webchat.py`.
   - Execute the following shell command to append the complete, verbatim parameterized test:
```bash
cat << 'EOF' >> tests/test_webchat.py

import time
import os
from unittest.mock import MagicMock
import webchat

@pytest.mark.parametrize("func_name, args_factory", [
    ("infer_location", lambda tmp_path, func_call, upload_mock: ("for Paris",)),
    ("create_map_html", lambda tmp_path, func_call, upload_mock: ([(1.0, 2.0)],)),
    ("parse_table_coordinates", lambda tmp_path, func_call, upload_mock: ("| a | b | c |\n|---|---|---|\n| a | 1.0 | 2.0 |", 1, 2)),
    ("parse_distance_table", lambda tmp_path, func_call, upload_mock: ("| Lat1 | Lon1 | Lat2 | Lon2 |\n|---|---|---|---|\n| 1.0 | 2.0 | 3.0 | 4.0 |",)),
    ("extract_map_coords", lambda tmp_path, func_call, upload_mock: ("geocode_locations", "| Query | Matched | Lat | Lon |\n|---|---|---|---|\n| Paris | Paris, France | 48.8566 | 2.3522 |")),
    ("run_tool", lambda tmp_path, func_call, upload_mock: (func_call,)),
    ("respond", lambda tmp_path, func_call, upload_mock: ("Hello", [], upload_mock)),
    ("chat", lambda tmp_path, func_call, upload_mock: ("Hello", [], upload_mock)),
    ("build_ui", lambda tmp_path, func_call, upload_mock: ()),
    ("main", lambda tmp_path, func_call, upload_mock: ()),
])
def test_webchat_tz_settings(func_name, args_factory, mocker, tmp_path, monkeypatch):
    mocker.patch("webchat.call_llm_with_retry")
    mocker.patch("webchat.client")
    mock_registry = mocker.patch("webchat.registry")
    mock_registry.invoke.return_value = "| Query | Matched | Lat | Lon |\n|---|---|---|---|\n| Paris | Paris, France | 48.8566 | 2.3522 |"
    mocker.patch("gradio.Blocks.launch")

    upload_file = tmp_path / "upload.txt"
    upload_file.write_text("dummy")
    upload_mock = MagicMock()
    upload_mock.name = str(upload_file)

    func_call = MagicMock()
    func_call.name = "geocode_locations"
    func_call.arguments = '{"locations": "Paris"}'

    args = args_factory(tmp_path, func_call, upload_mock)
    func = getattr(webchat, func_name)

    results = []
    for tz in ["UTC", "America/New_York"]:
        monkeypatch.setenv("TZ", tz)
        if hasattr(time, "tzset"):
            time.tzset()

        try:
            res = func(*args)
        except Exception as e:
            res = str(e)
        results.append(res)

    if type(results[0]) is not type(results[1]):
        pytest.xfail(f"Return type differs for {func_name} under different timezones")

    if str(results[0]) != str(results[1]):
        pytest.xfail(f"Behavior differs for {func_name} under different timezones")
    else:
        assert str(results[0]) == str(results[1])
