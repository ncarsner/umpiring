import configparser
from dataclasses import dataclass, field, InitVar
from datetime import datetime
import sqlite3
from sqlite3 import Error

import sites
import leagues
import googlemaps

config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["credentials"]["api_key"]
default_from = config["credentials"]["default_from"]

db_file = "officiating.db"


@dataclass
class Game:
    site: str
    league: str
    db_handler: InitVar["DatabaseHandler"]
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d"))
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
            distance_text = distance_result["rows"][0]["elements"][0]["distance"]["text"]
            if "km" in distance_text:
                distance_km = float(distance_text.split()[0].replace(",", ""))
                distance_miles = round(distance_km * 0.621371, 1)
                return distance_miles
            else:
                # Assuming the distance is in miles if "km" is not in distance_text
                return float(distance_text.split()[0])
        else:
            return 0.0

    def __post_init__(self, db_handler):
        self.assignor = self.get_assignor_from_league(self.league)
        self.game_fee = self.get_game_fee_from_league(self.league)
        # self.mileage = Game.calculate_distance_for_site(api_key, default_from, self.site, sites.ballfields)
        self.mileage = self.get_site_mileage_from_db(db_handler, self.site)

    @staticmethod
    def get_site_mileage_from_db(db_handler, site_name):
        mileage = db_handler.get_site_mileage(site_name)
        return mileage if mileage is not None else 0

    @staticmethod
    def get_game_fee_from_league(league):
        game_fees = leagues.game_rates
        return game_fees.get(league, 0)

    @staticmethod
    def get_assignor_from_league(league):
        league_assignors = leagues.game_assignors
        return league_assignors.get(league, "TBD")


class DatabaseHandler:
    # def __init__(self, db_file):
    #     self.db_file = db_file

    def __init__(self, db_file, api_key=api_key):
        self.db_file = db_file
        self.api_key = api_key
        self.gmaps = googlemaps.Client(key=self.api_key)

    def create_connection(self):
        """Create a database connection to a SQLite database"""
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)
        return None

    def initialize_database(self):
        """Initialize the database with the required tables"""
        conn = self.create_connection()
        if conn is not None:
            self.create_games_table(conn)
            self.create_relation_tables(conn)
            conn.close()
        else:
            print("Error! cannot create the database connection.")

    def create_games_table(self, conn):
        """Create a table in the SQLite database"""
        try:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    site TEXT,
                    league TEXT,
                    assignor TEXT,
                    game_fee INTEGER,
                    fee_paid BOOLEAN,
                    is_volunteer BOOLEAN,
                    mileage FLOAT
                );
            """
            )
            print("Table created successfully")
        except Error as e:
            print(e)

    def create_sites_table(self):
        conn = self.create_connection()
        if conn is not None:
            try:
                c = conn.cursor()
                c.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sites (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        mileage FLOAT DEFAULT 0
                    )
                """
                )
                conn.commit()
                print("Table created successfully")
            except Error as e:
                print(e)
            finally:
                conn.close()
        else:
            print("Error! Cannot create the database connection.")

    def create_relation_tables(self, conn):
        """Create or update relation tables in the SQLite database to include mileage in sites"""
        try:
            c = conn.cursor()
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    mileage INTEGER DEFAULT 0.0
                );
                CREATE TABLE IF NOT EXISTS leagues (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                );
                CREATE TABLE IF NOT EXISTS assignors (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                );
            """
            )
            print("Relation tables created or updated successfully")
        except sqlite3.Error as e:
            print(e)

    def drop_tables(self):
        """Drop tables from the database"""
        conn = self.create_connection()
        if conn is not None:
            try:
                c = conn.cursor()
                c.execute("DROP TABLE IF EXISTS games")
                c.execute("DROP TABLE IF EXISTS sites")
                c.execute("DROP TABLE IF EXISTS leagues")
                c.execute("DROP TABLE IF EXISTS assignors")
                conn.commit()
                print("Tables dropped successfully")
            except sqlite3.Error as e:
                print(f"An error occurred while dropping tables: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def rebuild_database(self):
        """Drops all tables and recreates them with the updated structure"""
        conn = self.create_connection()
        if conn is not None:
            try:
                c = conn.cursor()

                # Drop existing tables
                c.execute("DROP TABLE IF EXISTS games")
                c.execute("DROP TABLE IF EXISTS sites")
                c.execute("DROP TABLE IF EXISTS leagues")
                c.execute("DROP TABLE IF EXISTS assignors")
                # Recreate table with the updated schema

                self.create_games_table(conn)
                self.create_relation_tables(conn)

                conn.commit()
                print("Database rebuilt successfully")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def fetch_unpaid_game_ids(self):
        """Fetch IDs of unpaid games."""
        conn = self.create_connection()
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM games WHERE fee_paid = 0")
                unpaid_games = cur.fetchall()
                return [game[0] for game in unpaid_games]  # Return a list of IDs
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")
        return []

    def bulk_update_games_paid_status(self, game_ids, paid_status):
        """Bulk update the paid status of multiple games."""
        conn = self.create_connection()
        if conn is not None:
            try:
                cur = conn.cursor()
                # Prepare the SQL query to update the fee_paid status
                sql = "UPDATE games SET fee_paid = ? WHERE id IN ({seq})".format(seq=",".join(["?"] * len(game_ids)))
                # Execute the query with paid_status and the list of game_ids
                cur.execute(sql, [int(paid_status)] + game_ids)
                conn.commit()
                print(f"{cur.rowcount} games have been updated.")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def populate_site_distances(self, default_from=default_from, site_dict=sites.ballfields):
        conn = self.create_connection()
        if conn is not None:
            try:
                for site_name, address in site_dict.items():
                    distance_result = self.gmaps.distance_matrix(default_from, address, mode="driving")
                    if distance_result["rows"][0]["elements"][0]["status"] == "OK":
                        distance_text = distance_result["rows"][0]["elements"][0]["distance"]["text"]
                        distance_km = float(distance_text.split()[0].replace(",", ""))
                        if "km" in distance_text:
                            distance_miles = round(distance_km * 0.621371, 1)
                        else:
                            distance_miles = distance_km
                        with conn:
                            conn.execute(
                                "INSERT OR REPLACE INTO sites (name, mileage) VALUES (?, ?)",
                                (site_name, distance_miles),
                            )
                    else:
                        print(f"Distance not found for site: {site_name}")
                conn.commit()
            except Error as e:
                print(e)
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def get_site_mileage(self, site_name):
        conn = self.create_connection()
        mileage = None
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT mileage FROM sites WHERE name = ?", (site_name,))
                result = cursor.fetchone()
                if result:
                    mileage = result[0]
            except Error as e:
                print(e)
            finally:
                conn.close()
        return mileage

    def update_or_add_site(self, site_name, mileage):
        """Update mileage for an existing site or add a new site with its mileage."""
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                # Check if the site already exists
                cursor.execute("SELECT id FROM sites WHERE name = ?", (site_name,))
                site = cursor.fetchone()
                if site:
                    # Update mileage for the existing site
                    cursor.execute("UPDATE sites SET mileage = ? WHERE name = ?", (mileage, site_name))
                else:
                    # Insert a new site with mileage
                    cursor.execute("INSERT INTO sites (name, mileage) VALUES (?, ?)", (site_name, mileage))
                conn.commit()
                print(f"Site '{site_name}' updated/added successfully.")
            except sqlite3.Error as e:
                print(f"An error occurred while updating/adding the site: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def list_sites(self):
        """List all sites and their mileages from the sites table."""
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT name, mileage FROM sites ORDER BY name")
                sites = cursor.fetchall()
                for site in sites:
                    print(f"Site: {site[0]}, Mileage: {site[1]}")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")


db_handler = DatabaseHandler(db_file)

# Call API to populate sites milage in database
# db_handler.populate_site_distances()

# List all sites
# print(db_handler.list_sites())

# # Update mileage for an existing site or add a new site
# site_name = "Central Park"
# mileage = 12.5  # Example mileage
# db_handler.update_or_add_site(site_name, mileage)
