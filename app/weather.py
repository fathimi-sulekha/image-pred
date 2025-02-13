import json

def get_weather(arguments: str) -> dict:
    # Parse the JSON arguments
    args = json.loads(arguments)
    location = args.get("location")
    unit = args.get("unit", "fahrenheit")
    
    # Simulate fetching weather data
    # (Replace with real weather API logic if needed)
    weather_info = {
        "location": location,
        "temperature": 72,  # Dummy value
        "unit": unit,
        "forecast": "Sunny"
    }
    return weather_info
