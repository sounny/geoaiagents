"""Run this model in Python

> pip install openai
"""
import json
from openai import OpenAI
from geocode import geocode_locations  # import our geocoding tool

def main():
    # Initialize OpenAI client
    client = OpenAI(base_url="http://localhost:5272/v1/", api_key="unused")

    # Prompt the user for their request
    user_input = input(
        "Hello, I am Humboldt, your GeoAI Agent. How can I assist you today?\n"
    )

    # System prompt describing the agent's role
    system_prompt = (
        "You are a GeoAI Agent who is an expert GIS and Remote Sensing Analyst, "
        "cartographer, and Geospatial Developer. Your name is Humboldt, in honor "
        "of Alexander von Humboldt, the father of Modern Geography. You will "
        "take user needs, call upon specialized tools (like geocoding), and "
        "manage their inputs and outputs to fulfill the request."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    # Define available tool functions
    functions = [
        {
            "name": "geocode_locations",
            "description": "Geocode a list of locations and return a markdown table",
            "parameters": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited list of locations to geocode"
                    }
                },
                "required": ["locations"]
            }
        }
    ]

    # First LLM call with function support
    response = client.chat.completions.create(
        model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
        messages=messages,
        functions=functions,
        function_call="auto",
        max_tokens=1000,
        frequency_penalty=1,
    )
    message = response.choices[0].message

    # If the LLM chooses to call a function, execute it
    if message.function_call:
        args = json.loads(message.function_call.arguments)
        # Only one function now, geocode_locations
        table = geocode_locations(args["locations"])
        # Append the function call and result
        messages.append({"role": "assistant", "content": None, "function_call": message.function_call})
        messages.append({"role": "function", "name": message.function_call.name, "content": table})
        # Send back to LLM for final answer
        second_resp = client.chat.completions.create(
            model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
            messages=messages,
            max_tokens=1000,
            frequency_penalty=1,
        )
        print(second_resp.choices[0].message.content)
    else:
        # No function call: just print the assistant message
        print(message.content)

if __name__ == "__main__":
    main()