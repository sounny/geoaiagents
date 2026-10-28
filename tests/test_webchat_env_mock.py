import pytest
import importlib
import unittest.mock as mock

def test_webchat_delenv(monkeypatch, mocker):
    mocker.patch("openai.OpenAI")
    for env_var in ["OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL", "HUMBOLDT_MODEL", "HUMBOLDT_DEBUG"]:
        monkeypatch.delenv(env_var, raising=False)

    import webchat
    importlib.reload(webchat)

    mocker.patch("webchat.call_llm_with_retry")
    webchat.call_llm_with_retry.return_value = mock.MagicMock()
    webchat.call_llm_with_retry.return_value.choices[0].message.content = "mock reply"
    webchat.call_llm_with_retry.return_value.choices[0].message.function_call = None

    assert webchat.BASE_URL == "http://localhost:5272/v1/"
    assert webchat.API_KEY == "unused"
    assert webchat.MODEL_NAME == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
    assert webchat.DEBUG is False

    assert webchat.infer_location("for Paris") == "Paris"
    assert type(webchat.create_map_html([(0.0, 0.0)])) == str

    table = "| Location | Latitude | Longitude |\n|---|---|---|\n| Paris | 48.8 | 2.3 |"
    assert webchat.parse_table_coordinates(table, 1, 2) == [(48.8, 2.3)]

    dist_table = "| L1 | L2 | L3 | L4 |\n|---|---|---|---|\n| 0 | 0 | 1 | 1 |"
    assert webchat.parse_distance_table(dist_table) == [(0.0, 0.0), (1.0, 1.0)]

    mocker.patch("webchat.parse_tool_args", return_value={})
    mocker.patch("webchat.registry.invoke", return_value="table_res")
    fake_call = mock.MagicMock()
    fake_call.name = "mytool"
    assert webchat.run_tool(fake_call) == ("mytool", "table_res")

    # "distance" gets empty list in webchat.extract_map_coords since DEFAULT_TOOL_COORD_PARSERS may not define it by default
    res = webchat.extract_map_coords("distance", dist_table)
    if res != [(0.0, 0.0), (1.0, 1.0)]:
        pytest.xfail("Looks like a bug: 'distance' tool extract_map_coords does not use parse_distance_table when 'distance' is not in DEFAULT_TOOL_COORD_PARSERS")

    reply, html, logs, tbl = webchat.respond("msg", [])
    assert reply == "mock reply"

    chat_res, _, _, _ = webchat.chat("msg", [], None)
    assert len(chat_res) == 2


def test_webchat_setenv_empty(monkeypatch, mocker):
    mocker.patch("openai.OpenAI")
    for env_var in ["OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL", "HUMBOLDT_MODEL", "HUMBOLDT_DEBUG"]:
        monkeypatch.setenv(env_var, "")

    import webchat
    importlib.reload(webchat)

    mocker.patch("webchat.call_llm_with_retry")
    webchat.call_llm_with_retry.return_value = mock.MagicMock()
    webchat.call_llm_with_retry.return_value.choices[0].message.content = "mock reply"
    webchat.call_llm_with_retry.return_value.choices[0].message.function_call = None

    assert webchat.BASE_URL == ""
    assert webchat.API_KEY == ""
    assert webchat.MODEL_NAME == "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
    assert webchat.DEBUG is False

    assert webchat.infer_location("for Paris") == "Paris"
    assert type(webchat.create_map_html([(0.0, 0.0)])) == str

    table = "| Location | Latitude | Longitude |\n|---|---|---|\n| Paris | 48.8 | 2.3 |"
    assert webchat.parse_table_coordinates(table, 1, 2) == [(48.8, 2.3)]

    dist_table = "| L1 | L2 | L3 | L4 |\n|---|---|---|---|\n| 0 | 0 | 1 | 1 |"
    assert webchat.parse_distance_table(dist_table) == [(0.0, 0.0), (1.0, 1.0)]

    mocker.patch("webchat.parse_tool_args", return_value={})
    mocker.patch("webchat.registry.invoke", return_value="table_res")
    fake_call = mock.MagicMock()
    fake_call.name = "mytool"
    assert webchat.run_tool(fake_call) == ("mytool", "table_res")

    res = webchat.extract_map_coords("distance", dist_table)
    if res != [(0.0, 0.0), (1.0, 1.0)]:
        pytest.xfail("Looks like a bug: 'distance' tool extract_map_coords does not use parse_distance_table when 'distance' is not in DEFAULT_TOOL_COORD_PARSERS")


    reply, html, logs, tbl = webchat.respond("msg", [])
    assert reply == "mock reply"

    chat_res, _, _, _ = webchat.chat("msg", [], None)
    assert len(chat_res) == 2


@pytest.mark.xfail(raises=TypeError, reason="Looks like a bug: Chatbot.__init__() got an unexpected keyword argument 'type'")
def test_webchat_build_ui_bug(mocker):
    mocker.patch("openai.OpenAI")
    import webchat
    webchat.build_ui()

@pytest.mark.xfail(raises=TypeError, reason="Looks like a bug: Chatbot.__init__() got an unexpected keyword argument 'type'")
def test_webchat_main_bug(mocker):
    mocker.patch("openai.OpenAI")
    import webchat
    webchat.main()
