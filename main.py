import configparser
from dataclasses import dataclass, field
from datetime import datetime

import sites
import leagues
import googlemaps

config = configparser.ConfigParser()
config.read("config.ini")

api_key = config["credentials"]["api_key"]
default_from = config["credentials"]["default_from"]


@dataclass
class Game:
    site: str
    league: str
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    assignor: str = field(init=False)
    game_fee: int = field(init=False)
    fee_paid: bool = False
    is_volunteer: bool = False
    mileage: float = field(init=False)

    @staticmethod
    def calculate_distance_for_site(api_key, default_from, site_name, site_dict):
        gmaps = googlemaps.Client(key=api_key)
        address = site_dict.get(site_name)
        if not address:
            return "Site address not found"

        distance_result = gmaps.distance_matrix(default_from, address, mode="driving")
        if distance_result["rows"][0]["elements"][0]["status"] == "OK":
            distance_text = distance_result["rows"][0]["elements"][0]["distance"][
                "text"
            ]
            if "km" in distance_text:
                distance_km = float(distance_text.split()[0].replace(",", ""))
                distance_miles = round(distance_km * 0.621371, 1)
                return distance_miles
            else:
                # Assuming the distance is in miles if "km" is not in distance_text
                return float(distance_text.split()[0])
        else:
            return 0.0

    def __post_init__(self):
        self.assignor = self.get_assignor_from_league(self.league)
        self.game_fee = self.get_game_fee_from_league(self.league)
        # self.mileage = self.get_mileage_from_site(self.site)
        self.mileage = Game.calculate_distance_for_site(
            api_key, default_from, self.site, sites.ballfields
        )

    # @staticmethod
    # def get_mileage_from_site(site):
    #     ballparks = sites.ballfields
    #     return ballparks.get(site, 0)

    @staticmethod
    def get_game_fee_from_league(league):
        game_fees = leagues.game_rates
        return game_fees.get(league, 0)

    @staticmethod
    def get_assignor_from_league(league):
        league_assignors = leagues.game_assignors
        return league_assignors.get(league, "TBD")


class DatabaseHandler:
    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        pass

    def create_relation_tables(self):
        pass

    def drop_tables(self):
        pass

    def update_sites_with_missing_mileage(self):
        pass
