import json


def format_plus_codes(input_dict):
    """Formats the values in the input dictionary as compound codes."""
    formatted_dict = {}
    for key, value in input_dict.items():
        formatted_value = value.replace("+", "%2B").replace(" ", "%20").replace(",", "")
        formatted_dict[key] = formatted_value
    return formatted_dict


def format_single_plus_code(plus_code):
    """Formats a single Plus Code string."""
    return plus_code.replace("+", "%2B").replace(" ", "%20").replace(",", "")


def kilometers_to_miles(km):
    """Convert kilometers to miles."""
    miles = int(km * 0.621371 * 1000) / 1000
    return miles


def extract_distance_and_convert(json_data):
    """Extract the distance from the JSON and convert it to miles."""
    # Parse the JSON data
    data = json.loads(json_data)

    # Access the distance value from the API call
    meters = data["rows"][0]["elements"][0]["distance"]["value"]

    # Convert meters to kilometers
    kilometers = meters / 1000

    # Convert kilometers to miles
    miles = kilometers_to_miles(kilometers)

    return miles
