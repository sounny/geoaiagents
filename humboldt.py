"""Run this model in Python

> pip install openai
"""
import json
from openai import OpenAI
from geocode import geocode_locations  # import our geocoding tool
from dd2dms import convert_dd_to_dms  # import DD→DMS conversion tool

def main():
    client = OpenAI(base_url="http://localhost:5272/v1/", api_key="unused")

    # System prompt describing the agent's role and tool‐calling instructions
    system_prompt = (
        "You are Humboldt, a GeoAI Agent. When a user asks for geocoding or DD→DMS conversion,\n"
        "you MUST call the matching function (geocode_locations or convert_dd_to_dms) via function_call\n"
        "and return ONLY the tool’s output, without adding extra text yourself.\n"
        "If it’s a normal question, answer directly."
    )

    # Initialize chat history and tool schema once
    messages = [{"role": "system", "content": system_prompt}]
    functions = [
        {
            "name": "geocode_locations",
            "description": "Geocode a single address or a list of addresses and return a markdown table",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "A single address or newline/semicolon-delimited list of addresses"
                    }
                },
                "required": ["address"]
            }
        },
        {
            "name": "convert_dd_to_dms",
            "description": "Convert decimal-degree coordinates to DMS table",
            "parameters": {
                "type": "object",
                "properties": {
                    "coordinates": {
                        "type": "string",
                        "description": "Newline- or semicolon-delimited DD lat,lon pairs"
                    }
                },
                "required": ["coordinates"]
            }
        }
    ]

    # Greet the user
    print("Hi, I'm Humboldt, your GeoAI Agent. How can I assist you today?")
    # REPL loop
    while True:
        user_input = input("Humboldt> (type 'exit' to quit)\n")
        if user_input.lower() in ("exit", "quit"):
            print("Exiting Humboldt. Goodbye!")
            break

        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        print("[DEBUG] Sending to LLM:", messages)

        # First call (possibly function)
        response = client.chat.completions.create(
            model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
            messages=messages,
            functions=functions,
            function_call="auto",
            max_tokens=1000,
            frequency_penalty=1,
        )
        message = response.choices[0].message
        print("[DEBUG] LLM response:", message)

        # If LLM requested our geocode tool
        if message.function_call:
            args = json.loads(message.function_call.arguments)
            # Status notifications for tool invocation
            if message.function_call.name == "geocode_locations":
                print("Status: Invoking geocoding agent...")
                table = geocode_locations(args["address"])
            elif message.function_call.name == "convert_dd_to_dms":
                print("Status: Invoking DD to DMS conversion agent...")
                table = convert_dd_to_dms(args["coordinates"])
            # Log tool output
            print("[DEBUG] Tool output:\n", table)

            # Append the function call and its result to history
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": message.function_call
            })
            messages.append({
                "role": "function",
                "name": message.function_call.name,
                "content": table
            })

            # Second call to get the final assistant answer
            second_resp = client.chat.completions.create(
                model="Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx",
                messages=messages,
                max_tokens=1000,
                frequency_penalty=1,
            )
            print(second_resp.choices[0].message.content)

        else:
            # No tool call, just print the assistant reply
            print(message.content)

if __name__ == "__main__":
    main()