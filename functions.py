import sites

def format_compound_code(map_locations, place_name):
    """Format a compound Plus Code from the dictionary."""
    if place_name not in map_locations:
        raise ValueError(f"Location '{place_name}' not found in the dictionary")

    plus_code_with_location = map_locations[place_name]
    compound_code = plus_code_with_location.replace('+', '%2B').replace(' ', '%20')
    return compound_code

# Example usage
try:
    place_name = "Siegel HS"  # Replace with the place name you want to format
    formatted_compound_code = format_compound_code(sites.fields_and_plus_codes, place_name)
    print(f"{place_name} formatted as {formatted_compound_code}")
except ValueError as e:
    print(e)
