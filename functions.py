import json
import googlemaps


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


# Function to calculate distances using Google Maps API for a dictionary of addresses
def calculate_distances(api_key, default_from, destination_addresses):
    # Initialize the Google Maps client with your API key
    gmaps = googlemaps.Client(key=api_key)

    # Dictionary to hold the names and distances
    distances = {}

    # Iterate over the destination addresses dictionary
    for name, address in destination_addresses.items():
        # Get the distance matrix result
        distance_result = gmaps.distance_matrix(default_from, address, mode="driving")

        # Extract the distance if available
        if distance_result["rows"][0]["elements"][0]["status"] == "OK":
            distance_text = distance_result["rows"][0]["elements"][0]["distance"][
                "text"
            ]
            # Check if the distance is in miles, otherwise convert it
            if "km" in distance_text:
                # Extract the numeric part and convert it to miles (1 km = 0.621371 miles)
                distance_km = float(distance_text.split()[0].replace(",", ""))
                distance_miles = round(distance_km * 0.621371, 1)
                distances[name] = f"{distance_miles} miles"
            else:
                distances[name] = distance_text
        else:
            distances[name] = "Distance not found"

    return distances
