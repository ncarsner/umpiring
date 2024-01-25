import configparser
from dataclasses import dataclass, field
from datetime import datetime

import functions
import sites
import leagues

config = configparser.ConfigParser()
config.read("config.ini")

api_key = config["credentials"]["api_key"]
default_from = config["credentials"]["default_from"]

# selected_site = random.choice(format_plus_codes(sites.fields_and_plus_codes.values()))
# sites_api_formatted = functions.format_plus_codes(sites.fields_and_plus_codes)
# selected_site = random.choice(list(sites_api_formatted.values()))

# print(selected_site)

# api_request = f"https://maps.googleapis.com/maps/api/distancematrix/json\
# ?destinations={selected_site}\
# &origins={functions.format_single_plus_code(default_from)}\
# &key={api_key}"

# print(api_request)


# # Calculate distances
# distances = functions.calculate_distances(api_key, default_from, sites.ballfields)

# # Print distances
# for name, distance in distances.items():
#     print(f"{name}: {distance}")


@dataclass
class Game:
    # Attributes with default values
    date: datetime = field(default_factory=lambda: datetime.today())
    site: str = ""
    league: str = ""
    assignor: str = ""
    game_fee: int = 0
    fee_paid: bool = False
    is_volunteer: bool = False

    # Mileage attribute will be calculated based on the 'site'
    def __post_init__(self):
        self.mileage = self.get_mileage_from_site(self.site)

    @staticmethod
    def get_mileage_from_site(site):
        # Define the dictionary of ballparks and their corresponding mileages
        ballparks = sites.ballfields
        # Return the mileage for the given site, or 0 if the site is not found
        return ballparks.get(site, 0)
    
    @staticmethod
    def get_game_fee_from_league(league):
        # Define the leagues and their corresponding game fees
        game_fees = leagues.game_rates
        return game_fees.get(league, 0)
    
    @staticmethod
    def get_assigor_from_league(league):
        # Define the leagues and their corresponding assignors
        league_assignors = leagues.game_assignors
        return league_assignors.get(league, 0)
