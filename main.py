import configparser
import sites
import random
import functions

config = configparser.ConfigParser()
config.read("config.ini")

api_key = config["credentials"]["api_key"]
default_from = config["credentials"]["default_from"]

# selected_site = random.choice(format_plus_codes(sites.fields_and_plus_codes.values()))
sites_api_formatted = functions.format_plus_codes(sites.fields_and_plus_codes)
selected_site = random.choice(list(sites_api_formatted.values()))

# print(selected_site)

# api_request = f"https://maps.googleapis.com/maps/api/distancematrix/json\
# ?destinations={selected_site}\
# &origins={functions.format_single_plus_code(default_from)}\
# &key={api_key}"

# print(api_request)


# Calculate distances
distances = functions.calculate_distances(api_key, default_from, sites.ballfields)

# Print distances
for name, distance in distances.items():
    print(f"{name}: {distance}")
