import configparser
from dataclasses import dataclass, field
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
        self.mileage = Game.calculate_distance_for_site(
            api_key, default_from, self.site, sites.ballfields
        )

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
        """Create a database connection to a SQLite database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            # print(f"SQLite DB connected: version {sqlite3.version}")
            return conn
        except Error as e:
            print(e)
        return conn

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

    def create_mileage_table(self, conn):
        """Create a table in the SQLite database"""
        try:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS mileage (
                    id INTEGER PRIMARY KEY autoincrement,
                    name TEXT NOT NULL,
                    mileage FLOAT,
                    UNIQUE(name)
                );
            """
            )
            print("Table created successfully")
        except Error as e:
            print(e)

    def create_relation_tables(self, conn):
        """Create or update relation tables in the SQLite database to include mileage in sites"""
        try:
            c = conn.cursor()
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
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
                # SQL commands to drop tables
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
                print(f"An error occurred while rebuilding the database: {e}")
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
                sql = "UPDATE games SET fee_paid = ? WHERE id IN ({seq})".format(
                    seq=",".join(["?"] * len(game_ids))
                )
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
