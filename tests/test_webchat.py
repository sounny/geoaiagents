import pytest
import gradio as gr
import webchat

def test_respond_oversized_payload():
    large_message = "A" * 15001
    with pytest.raises(gr.Error, match="Message payload too large"):
        webchat.respond(large_message, [])
