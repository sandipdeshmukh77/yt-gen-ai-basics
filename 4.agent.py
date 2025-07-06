from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json
# client = OpenAI()

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def detect_location(_):
    print("⛏️ Tool called : detect_location")
    try:
        resp = requests.get("https://ipinfo.io/json")
        data = resp.json()
        city = data.get("city", "Unknown")
        country = data.get("country", "Unknown")
        return f"{city}, {country}"
    except Exception as e:
        return f"Could not detect location: {e}"

def get_weather(city: str):
    print(f"Tool Called: get_weather({city})")
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url)
        if response.status_code != 200:
            return f"Weather not found for {city}."
        return f"Weather in {city}: {response.text.strip()}"
    except Exception as e:
        return f"Could not get weather: {e}"
    
def create_plan(input_data):
    print(f"⛏️ Tool called : create_plan for {input_data}")
    location = input_data.get("location")
    weather = input_data.get("weather")
    # Use LLM to generate travel plan
    prompt = f"""You are a travel assistant. Create a full travel plan for {location} 
                  considering the following weather: {weather}. "
                  Be concise and practical."""
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    plan = response.choices[0].message.content.strip()
    return plan

# Tool registry
available_tools = {
    "detect_location": {
        "fn": detect_location,
        "description": "Detects the user's current location. Input: null. Output: string (location)."
    },
    "get_weather": {
        "fn": get_weather,
        "description": "Gets the current weather for a location. Input: string (location). Output: string (weather description)."
    },
    "create_plan": {
        "fn": create_plan,
        "description": "Creates a travel plan based on location and weather. Input: {\"location\": string, \"weather\": string}. Output: string (plan)."
    }
}


system_prompt = f"""
You are a helpful AI travel agent.
You operate in a loop of plan --> action --> observe --> output.
For the given user query, reason step-by-step and use the available tools as needed.

Available Tools:
{json.dumps({k: v["description"] for k, v in available_tools.items()}, indent=2)}

Instructions:
- Always respond with one JSON object per step.
- Wait for the observation after an action before proceeding.
- Carefully analyze the user request and think step-by-step.
- Use the available tools responsibly to complete the task.
- Check for errors in tool outputs.

Output JSON Format:
{{
    "step": "plan" | "action" | "observe" | "output",
    "content": "string",
    "function": "name of function (only for action step)",
    "input": "input for the function (only for action step)"
}}

Example:
{{ "step": "plan", "content": "User wants a travel plan for their current location." }}
{{ "step": "action", "function": "detect_location", "input": null }}
{{ "step": "observe", "content": "Pune, IN" }}
{{ "step": "action", "function": "get_weather", "input": "Pune, IN" }}
{{ "step": "observe", "content": "Weather in Pune, IN: clear sky, 22°C" }}
{{ "step": "action", "function": "create_plan", "input": "{{'location': 'Pune, IN', 'weather': 'clear sky, 22°C'}}" }}
{{ "step": "observe", "content": "Here is your plan for Pune, IN: ..."}}
{{ "step": "output", "content": "Here is your plan for Pune, IN: ..."}}
"""

history= []
system_prompt = system_prompt
history.append({
            "role": "system",
            "content": system_prompt
        })

while True:
    user_input = input(" 👤You: ")
    while True:
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot. Goodbye!")
            break
        user_input_with_role = {
                "role": "user",
                "content": user_input
            }
        history.append(user_input_with_role)

        response = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"}, #error
        messages=history)
        
        parsed_output = json.loads(response.choices[0].message.content)
        history.append({ "role": "assistant", "content": json.dumps(parsed_output) }) #error
        step = parsed_output.get("step")

        if step == "plan":
            print(f"🤔system -: {parsed_output.get('content')}")
            continue

        if step == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if tool_name in available_tools:
                    result = available_tools[tool_name]["fn"](tool_input)
                    history.append({
                        "role": "assistant",
                        "content": json.dumps({ "step": "observe", "content": result })
                    })
                    continue


        if step == "observe":
            print(f"🥸system -: {parsed_output.get('content')}")
            continue

        if step == "output":
            print(f"🤖system -: {parsed_output.get('content')}")
            break
    
