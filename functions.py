import json
import sqlite3
from sqlite3 import Error

import googlemaps


def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("SQLite DB connected: version", sqlite3.version)
        return conn
    except Error as e:
        print(e)
    return conn


def create_table(conn):
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
                game_fee REAL,
                fee_paid BOOLEAN,
                is_volunteer BOOLEAN,
                mileage INTEGER
            );
        """
        )
        print("Table created successfully")
    except Error as e:
        print(e)


def initialize_database(db_file):
    """Initialize the database with the required tables"""
    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")


# Initialize the database
db_file = "officiating.db"
initialize_database(db_file)


def create_relation_tables_v2(conn):
    """Create or update relation tables in the SQLite database to include mileage in sites"""
    try:
        c = conn.cursor()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                mileage INTEGER DEFAULT 0
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


def insert_site_if_not_exists(conn, site_name, mileage=0):
    """Insert a site into the sites table if it does not already exist and return its ID and mileage"""
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO sites(name, mileage) VALUES(?, ?)",
            (site_name, mileage),
        )
        cur.execute("SELECT id, mileage FROM sites WHERE name = ?", (site_name,))
        site_data = cur.fetchone()
        conn.commit()
        return site_data  # Returns a tuple (id, mileage)
    except sqlite3.Error as e:
        print(e)
        return None


def add_game_to_db_v3(db_file, game):
    """Add a game to the database with normalized tables and mileage logic"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            # Insert site if it doesn't exist and get its ID and mileage
            site_data = insert_site_if_not_exists(conn, game.site, game.mileage)
            site_id, site_mileage = site_data if site_data else (None, 0)

            # Use the mileage from the site if not provided in the game
            game_mileage = game.mileage if game.mileage > 0 else site_mileage

            # Prepare SQL to insert the game
            sql = """ INSERT INTO games(date, site_id, league_id, assignor_id, game_fee, fee_paid, is_volunteer, mileage)
                      VALUES(?,?,?,?,?,?,?,?) """
            cur = conn.cursor()
            cur.execute(
                sql,
                (
                    game.date.strftime("%Y-%m-%d"),
                    site_id,
                    game.league_id,
                    game.assignor_id,
                    game.game_fee,
                    game.fee_paid,
                    game.is_volunteer,
                    game_mileage,
                ),
            )
            conn.commit()
            print("Game added successfully")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


# def format_plus_codes(input_dict):
#     """Formats the values in the input dictionary as compound codes."""
#     formatted_dict = {}
#     for key, value in input_dict.items():
#         formatted_value = value.replace("+", "%2B").replace(" ", "%20").replace(",", "")
#         formatted_dict[key] = formatted_value
#     return formatted_dict


# def format_single_plus_code(plus_code):
#     """Formats a single Plus Code string."""
#     return plus_code.replace("+", "%2B").replace(" ", "%20").replace(",", "")


# def kilometers_to_miles(km):
#     """Convert kilometers to miles."""
#     miles = int(km * 0.621371 * 1000) / 1000
#     return miles


# def extract_distance_and_convert(json_data):
#     """Extract the distance from the JSON and convert it to miles."""
#     # Parse the JSON data
#     data = json.loads(json_data)

#     # Access the distance value from the API call
#     meters = data["rows"][0]["elements"][0]["distance"]["value"]

#     # Convert meters to kilometers
#     kilometers = meters / 1000

#     # Convert kilometers to miles
#     miles = kilometers_to_miles(kilometers)

#     return miles


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




def get_sites_with_zero_mileage(db_file):
    """ Retrieve sites with 0 mileage from the database """
    conn = create_connection(db_file)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sites WHERE mileage = 0")
        sites = cur.fetchall()
        return [site[0] for site in sites]
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()
    return []

def update_site_mileage(db_file, site_name, mileage):
    """ Update the mileage for a given site in the database """
    conn = create_connection(db_file)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE sites SET mileage = ? WHERE name = ?", (mileage, site_name))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()

def update_zero_mileage_sites(db_file, api_key, default_from):
    """ Update sites with 0 mileage using Google Maps API """
    sites = get_sites_with_zero_mileage(db_file)
    if sites:
        destination_addresses = {site: site for site in sites}  # Assuming site name is the address
        distances = calculate_distances(api_key, default_from, destination_addresses)

        for site, distance in distances.items():
            if "miles" in distance:
                mileage = float(distance.split()[0])
                update_site_mileage(db_file, site, mileage)
                print(f"Updated mileage for {site}: {mileage} miles")
            else:
                print(f"Distance not found for {site}")

# # Example usage
# db_file = 'officiating.db'
# api_key = 'YOUR_GOOGLE_MAPS_API_KEY'
# default_from = 'Your Default Address'
# update_zero_mileage_sites(db_file, api_key, default_from)

