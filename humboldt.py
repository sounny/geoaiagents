"""Run this model in Python

> pip install openai
"""

import argparse
import os
import logging
import subprocess
import sys
import importlib.util


def check_and_install_dependencies():
    """Check if required dependencies are installed and install them if missing."""
    print("Checking dependencies...")

    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"Warning: {requirements_file} not found. Assuming dependencies are installed.")
        return

    missing_packages = []

    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (remove version specifiers)
                package_name = line.split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                if not is_package_installed(package_name):
                    missing_packages.append(line)

    if missing_packages:
        print(f"Missing packages found: {', '.join(missing_packages)}")
        print("Installing missing dependencies...")

        for package in missing_packages:
            try:
                print(f"Installing {package}...")
                # Prefer --user for managed environments
                subprocess.run([sys.executable, "-m", "pip", "install", "--user", package],
                               check=True, capture_output=True, text=True)
                print(f"✓ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {package} with --user flag")
                try:
                    print(f"Trying alternative installation for {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", package],
                                   check=True, capture_output=True, text=True)
                    print(f"✓ Successfully installed {package}")
                except subprocess.CalledProcessError as e2:
                    if e.stderr:
                        print(f"Error details: {e.stderr}")
                    if e.stdout:
                        print(f"Output: {e.stdout}")
                    print("\nAutomatic installation failed. Please install dependencies manually:")
                    print("Option 1: pip install --user -r requirements.txt")
                    print("Option 2: pip install --break-system-packages -r requirements.txt")
                    print("Option 3: Create a virtual environment:")
                    print("  python3 -m venv venv")
                    print("  source venv/bin/activate")
                    print("  pip install -r requirements.txt")
                    sys.exit(1)

        print("All dependencies installed successfully!")
    else:
        print("All dependencies are already installed.")


def is_package_installed(package_name):
    """Check if a package is installed."""
    package_mapping = {
        'openai': 'openai',
        'geopy': 'geopy'
    }
    check_name = package_mapping.get(package_name, package_name)
    try:
        spec = importlib.util.find_spec(check_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


# Import modules that are definitely available; others imported after deps

def main():
    parser = argparse.ArgumentParser(description="Interactive GeoAI agent")
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENAI_BASE_URL", "http://localhost:5272/v1/"),
        help="OpenAI API base URL",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY", "unused"),
        help="OpenAI API key",
    )
    parser.add_argument(
        "--model",
        default=(
            os.getenv("OPENAI_MODEL")
            or os.getenv("HUMBOLDT_MODEL")
            or "Phi-4-mini-cpu-int4-rtn-block-32-acc-level-4-onnx"
        ),
        help="Model name to use",
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip automatic dependency checking and installation",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("HUMBOLDT_MAX_STEPS", 3)),
        help="Max consecutive tool calls before stopping (default: 3)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("HUMBOLDT_DEBUG", "0") in ("1", "true", "True"),
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if not args.skip_deps:
        check_and_install_dependencies()

    # Import modules after dependency checking
    try:
        from openai import OpenAI
        from tool_registry import create_registry
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed by running:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    system_prompt = (
        "You are a GeoAI Agent who is an expert GIS and Remote Sensing Analyst, "
        "cartographer, and Geospatial Developer. Your name is Humboldt, in honor "
        "of Alexander von Humboldt, the father of Modern Geography. You must "
        "always use the provided function tools to perform geospatial tasks and "
        "never guess results. When you invoke a tool it will be logged for the "
        "user to see. If the user requests a map marker or location to be shown, "
        "call `geocode_locations` first so the interface can display the point. "
        "Do not claim you are unable to manipulate maps or geospatial data; use "
        "the provided tools and let the interface handle map updates."
    )

    messages = [{"role": "system", "content": system_prompt}]
    tool_registry = create_registry()
    functions = tool_registry.openai_functions()

    def run_tool_call(tool_name: str, raw_args):
        if args.debug:
            print(f"[DEBUG] Requested tool: {tool_name} with args: {raw_args}")
        if not tool_registry.has_tool(tool_name):
            print(f"[WARN] Unknown tool requested: {tool_name}")
            return None
        return tool_registry.invoke(tool_name, raw_args)

    # Greet the user
    print("Hi, I'm Humboldt, your GeoAI Agent. How can I assist you today?")
    if args.debug:
        print("[DEBUG] Using model:", args.model)

    # REPL loop
    while True:
        user_input = input("Humboldt> (type 'exit' to quit)\n")
        if user_input.lower() in ("exit", "quit"):
            print("Exiting Humboldt. Goodbye!")
            break

        # Direct tool invocations
        if user_input.startswith("/geocode "):
            payload = user_input[len("/geocode "):]
            print(tool_registry.invoke("geocode_locations", {"locations": payload}))
            continue
        if user_input.startswith("/reverse "):
            payload = user_input[len("/reverse "):]
            print(tool_registry.invoke("reverse_geocode_coordinates", {"coordinates": payload}))
            continue
        if user_input.startswith("/dms "):
            payload = user_input[len("/dms "):]
            print(tool_registry.invoke("convert_dd_to_dms", {"coordinates": payload}))
            continue
        if user_input.startswith("/distance "):
            payload = user_input[len("/distance "):]
            print(tool_registry.invoke("calculate_distance", {"coordinates": payload}))
            continue

        messages.append({"role": "user", "content": user_input})
        if args.debug:
            print("[DEBUG] Sending to LLM (last 2 msgs):", messages[-2:])

        # Multi-step tool loop
        steps = 0
        last_content_printed = False
        while steps <= args.max_steps:
            response = client.chat.completions.create(
                model=args.model,
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=1000,
                frequency_penalty=1,
            )
            message = response.choices[0].message
            if args.debug:
                print("[DEBUG] LLM message:", message)

            if getattr(message, "function_call", None):
                call = message.function_call
                tool_output = run_tool_call(call.name, call.arguments)
                messages.append({"role": "assistant", "content": None, "function_call": call})
                messages.append({"role": "function", "name": call.name, "content": tool_output or ""})
                steps += 1
                continue

            if message.content:
                print(message.content)
                last_content_printed = True
                break

            break

        if steps > args.max_steps and not last_content_printed:
            print("[INFO] Reached maximum tool-call steps. Stopping.")

        if len(messages) > 20:
            messages = [messages[0]] + messages[-19:]


if __name__ == "__main__":
    main()
