import sqlite3
from sqlite3 import Error
from prettytable import PrettyTable
import sys

import googlemaps


db_file = "officiating.db"


def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        # print(f"SQLite DB connected: version {sqlite3.version}")
        return conn
    except Error as e:
        print(e)
    return conn


def drop_tables(db_file):
    """Drop tables from the database"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            c = conn.cursor()
            # SQL commands to drop tables
            # c.execute("DROP TABLE IF EXISTS games")
            c.execute("TRUNCATE TABLE IF EXISTS sites")
            c.execute("TRUNCATE TABLE IF EXISTS leagues")
            c.execute("TRUNCATE TABLE IF EXISTS assignors")
            conn.commit()
            print("Tables dropped successfully")
        except sqlite3.Error as e:
            print(f"An error occurred while dropping tables: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


# drop_tables(db_file)


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
                game_fee INT,
                fee_paid BOOLEAN,
                is_volunteer BOOLEAN,
                mileage REAL
            );
        """
        )
        print("Table created successfully")
    except Error as e:
        print(e)


def create_games_table(conn):
    """Create the 'games' table with the correct schema including 'site_id'"""
    try:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                date TEXT,
                site_id INTEGER,
                league_id INTEGER,
                assignor_id INTEGER,
                game_fee INTEGER,
                fee_paid BOOLEAN,
                is_volunteer BOOLEAN,
                mileage FLOAT,
                FOREIGN KEY (site_id) REFERENCES sites (id),
                FOREIGN KEY (league_id) REFERENCES leagues (id),
                FOREIGN KEY (assignor_id) REFERENCES assignors (id)
            );
        """
        )
        print("Games table created successfully")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def initialize_database(db_file):
    """Initialize the database with the required tables"""
    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn)
        create_relation_tables(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")


def create_relation_tables(conn):
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


def exit_application():
    print("Exiting the application.")
    sys.exit()


# def insert_site_if_not_exists(conn, site_name, mileage=0):
#     """Insert a site into the sites table if it does not already exist and return its ID and mileage"""
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             "INSERT OR IGNORE INTO sites(name, mileage) VALUES(?, ?)",
#             (site_name, mileage),
#         )
#         cur.execute("SELECT id, mileage FROM sites WHERE name = ?", (site_name,))
#         site_data = cur.fetchone()
#         conn.commit()
#         return site_data  # Returns a tuple (id, mileage)
#     except sqlite3.Error as e:
#         print(e)
#         return None


def insert_site_if_not_exists(conn, site_name, mileage=0):
    """Insert a site into the sites table if it does not already exist and return its ID"""
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO sites(name, mileage) VALUES(?, ?)",
            (site_name, mileage),
        )
        cur.execute("SELECT id FROM sites WHERE name = ?", (site_name,))
        site_id = cur.fetchone()[0]
        conn.commit()
        return site_id  # Return only site_id
    except sqlite3.Error as e:
        print(e)
        return None


# def get_league_id(conn, league_name):
#     """ Get the ID of a league from its name """
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM leagues WHERE name = UPPER(?)", (league_name,))
#     result = cur.fetchone()
#     return result[0] if result else None

# def get_assignor_id(conn, assignor_name):
#     """ Get the ID of an assignor from its name """
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM assignors WHERE name = UPPER(?)", (assignor_name,))
#     result = cur.fetchone()
#     return result[0] if result else None


def insert_league_if_not_exists(conn, league_name):
    """Insert a league into the leagues table if it does not already exist and return its ID"""
    try:
        cur = conn.cursor()
        # Convert league name to uppercase before inserting
        league_name = league_name.upper()
        cur.execute("INSERT OR IGNORE INTO leagues(name) VALUES(?)", (league_name,))
        cur.execute("SELECT id FROM leagues WHERE name = ?", (league_name,))
        league_id = cur.fetchone()[0]
        conn.commit()
        return league_id
    except sqlite3.Error as e:
        print(e)
        return None


def insert_assignor_if_not_exists(conn, assignor_name):
    """Insert an assignor into the assignors table if it does not already exist and return its ID"""
    try:
        cur = conn.cursor()
        # Convert assignor name to uppercase before inserting
        assignor_name = assignor_name.upper()
        cur.execute("INSERT OR IGNORE INTO assignors(name) VALUES(?)", (assignor_name,))
        cur.execute("SELECT id FROM assignors WHERE name = ?", (assignor_name,))
        assignor_id = cur.fetchone()[0]
        conn.commit()
        return assignor_id
    except sqlite3.Error as e:
        print(e)
        return None


# def add_game_to_db(db_file, game):
#     conn = create_connection(db_file)
#     if conn is not None:
#         try:
#             site_id = insert_site_if_not_exists(conn, game.site, game.mileage)
#             league_id = get_league_id(conn, game.league)
#             assignor_id = get_assignor_id(conn, game.assignor)

#             # Debugging: Print values and types
#             print("site_id:", site_id, type(site_id))
#             print("league_id:", league_id, type(league_id))
#             print("assignor_id:", assignor_id, type(assignor_id))

#             # Ensure IDs are not None
#             if site_id is None or league_id is None or assignor_id is None:
#                 raise ValueError("Site, league, or assignor ID not found.")

#             sql = """ INSERT INTO games(date, site_id, league_id, assignor_id, game_fee, fee_paid, is_volunteer, mileage)
#                       VALUES(?,?,?,?,?,?,?,?) """
#             cur = conn.cursor()
#             cur.execute(
#                 sql,
#                 (
#                     game.date,
#                     site_id,
#                     league_id,
#                     assignor_id,
#                     game.game_fee,
#                     game.fee_paid,
#                     game.is_volunteer,
#                     game.mileage,
#                 ),
#             )
#             conn.commit()
#             print("Game added successfully")
#         except sqlite3.Error as e:
#             print(e)
#         finally:
#             conn.close()
#     else:
#         print("Error! cannot create the database connection.")


# def add_game_to_db_v3(db_file, game):
#     conn = create_connection(db_file)
#     if conn is not None:
#         try:
#             site_id = insert_site_if_not_exists(conn, game.site, game.mileage)
#             league_id = get_league_id(conn, game.league)
#             assignor_id = get_assignor_id(conn, game.assignor)

#             # Debugging: Print values and types
#             print("site_id:", site_id, type(site_id))
#             print("league_id:", league_id, type(league_id))
#             print("assignor_id:", assignor_id, type(assignor_id))

#             sql = """ INSERT INTO games(date, site_id, league_id, assignor_id, game_fee, fee_paid, is_volunteer, mileage)
#                       VALUES(?,?,?,?,?,?,?,?) """
#             cur = conn.cursor()
#             cur.execute(
#                 sql,
#                 (
#                     game.date,
#                     site_id,
#                     league_id,
#                     assignor_id,
#                     game.game_fee,
#                     game.fee_paid,
#                     game.is_volunteer,
#                     game.mileage,
#                 ),
#             )
#             conn.commit()
#             print("Game added successfully")
#         except sqlite3.Error as e:
#             print(e)
#         finally:
#             conn.close()
#     else:
#         print("Error! cannot create the database connection.")


def add_game_to_db_v4(db_file, game):
    conn = create_connection(db_file)
    if conn is not None:
        try:
            if not game.site or not game.league:
                raise ValueError("Site and League required.")

            sql = """ INSERT INTO games(date, site, league, assignor, game_fee, fee_paid, is_volunteer, mileage)
                      VALUES(?,?,UPPER(?),?,?,?,?,?) """
            cur = conn.cursor()
            cur.execute(
                sql,
                (
                    game.date,
                    game.site,
                    game.league,
                    game.assignor,
                    game.game_fee,
                    game.fee_paid,
                    game.is_volunteer,
                    game.mileage,
                ),
            )
            conn.commit()
            print("Game added successfully")
        except sqlite3.Error as e:
            print(e)
        except ValueError as ve:
            print(ve)
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


def display_season_summary(db_file):
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cur = conn.cursor()
            # SQL query to sum games, fees, and mileage, grouped by assignor and league
            sql = """
                SELECT assignor, league, COUNT(*) as total_games, 
                       SUM(game_fee) as total_fees, SUM(mileage) as total_mileage
                FROM games
                GROUP BY assignor, league
            """
            cur.execute(sql)
            summary = cur.fetchall()

            if summary:
                table = PrettyTable()
                table.field_names = [
                    "Assignor",
                    "League",
                    "Total Games",
                    "Total Fees",
                    "Total Mileage",
                ]

                for row in summary:
                    table.add_row(row)

                print("Season Summary:\n")
                print(table)
            else:
                print("No data found.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


# Function to calculate distances using Google Maps API for a dictionary of addresses
def calculate_distances(api_key, default_from, destination_addresses):
    gmaps = googlemaps.Client(key=api_key)

    distances = {}

    # Iterate over the destination addresses dictionary
    for name, address in destination_addresses.items():
        # Get the distance matrix result
        distance_result = gmaps.distance_matrix(default_from, address, mode="driving")

        if distance_result["rows"][0]["elements"][0]["status"] == "OK":
            distance_text = distance_result["rows"][0]["elements"][0]["distance"][
                "text"
            ]
            # Convert from km to miles
            if "km" in distance_text:
                distance_km = float(distance_text.split()[0].replace(",", ""))
                distance_miles = round(distance_km * 0.621371, 1)
                distances[name] = f"{distance_miles} miles"
            else:
                distances[name] = distance_text
        else:
            distances[name] = "Distance not found"

    return distances


def get_sites_with_zero_mileage(db_file):
    """Retrieve sites with 0 mileage from the database"""
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
    """Update the mileage for a given site in the database"""
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
    """Update sites with 0 mileage using Google Maps API"""
    sites = get_sites_with_zero_mileage(db_file)
    if sites:
        destination_addresses = {
            site: site for site in sites
        }  # Assuming site name is the address
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


def review_unpaid_games(db_file):
    """Function to review unpaid games, with specific fields"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cur = conn.cursor()
            # Adjusted SQL query to select specific fields
            # sql = """ SELECT g.date, s.name, g.league_id, g.assignor_id, g.game_fee
            #           FROM games g
            #           JOIN sites s ON g.site_id = s.id
            #           WHERE g.fee_paid = 0 """
            sql = """ 
                SELECT g.id, g.date, g.site, g.league, 
                       g.assignor, g.game_fee, g.fee_paid
                FROM games g
                WHERE g.fee_paid = 0
            """
            cur.execute(sql)
            # cur.execute(
            #     "SELECT id, date, site, league, assignor, game_fee FROM games WHERE fee_paid = 0"
            # )
            # Fetch and display the results
            unpaid_games = cur.fetchall()

            if unpaid_games:
                table = PrettyTable()
                # Set column names for the selected fields
                table.field_names = [
                    "ID",
                    "Date",
                    "Site",
                    "League",
                    "Assignor",
                    "Game Fee",
                    "Paid",
                ]

                for game in unpaid_games:
                    table.add_row(game)

                print(table)
            else:
                print("No unpaid games found.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


def update_game_by_id(db_file):
    conn = create_connection(db_file)
    if conn is not None:
        try:
            game_id = input("Enter the ID of the game to update: ")
            print("Which field would you like to update?")
            print("[D]ate")
            print("[S]ite")
            print("[L]eague")
            print("[A]ssignor")
            print("[G]ame Fee")
            print("[F]ee Paid")
            print("[V]olunteer")
            print("[M]ileage")
            field = input("Enter the number of the field: ").lower()

            # Define a dictionary to map user input to database columns
            fields_map = {
                "d": "date",
                "s": "site",
                "l": "league",
                "a": "assignor",
                "g": "game_fee",
                "f": "fee_paid",
                "v": "is_volunteer",
                "m": "mileage",
            }

            if field in fields_map:
                new_value = input(f"Enter the new value for {fields_map[field]}: ")
                if field in ["5", "8"]:  # Assuming game_fee and mileage are numeric
                    new_value = float(new_value)
                if field in [
                    "6",
                    "7",
                ]:  # Assuming fee_paid and is_volunteer are boolean
                    new_value = new_value.lower() in ["yes", "true", "1"]

                # Prepare the SQL query
                sql = f"UPDATE games SET {fields_map[field]} = ? WHERE id = ?"
                cur = conn.cursor()
                cur.execute(sql, (new_value, game_id))
                conn.commit()
                print(f"Game with ID {game_id} has been updated.")
            else:
                print("Invalid field selection.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


def database_operations_submenu():
    db_operations = {
        "r": return_to_main_menu,
        "t": drop_tables,
        "c": create_relation_tables,
        "u": update_sites_with_missing_mileage,
        "d": rebuild_database,
    }

    while True:
        print("\nDatabase Operations")
        print("[R]eturn to Main Menu")
        print("[T]runcate ancillary tables")
        print("[C]reate relational tables")
        print("[U]pdate Sites with missing mileage")
        print("[D]rop and rebuild database\n")
        choice = input("Enter your choice: ").lower()

        if choice == "r":
            break
        elif choice in db_operations:
            confirmation = input("Are you sure?? (yes/no) ").lower()
            if confirmation == "yes":
                db_operations[choice]()
        else:
            print("Invalid choice. Please try again.")


def update_sites_with_missing_mileage():
    # This function should handle the logic of updating the sites table
    # by querying the API for missing mileage values and updating the database.
    pass


def return_to_main_menu():
    # This function simply breaks the loop in the database_operations_submenu
    # to return to the main menu.
    pass


def rebuild_database(db_file):
    """Drops all tables and recreates them with the updated structure"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            c = conn.cursor()

            # Drop existing tables
            c.execute("DROP TABLE IF EXISTS games")
            c.execute("DROP TABLE IF EXISTS sites")
            c.execute("DROP TABLE IF EXISTS leagues")
            c.execute("DROP TABLE IF EXISTS assignors")

            # Recreate tables with the updated schema
            c.execute(
                """ 
                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    mileage FLOAT DEFAULT 0
                )
            """
            )
            c.execute(
                """ 
                CREATE TABLE IF NOT EXISTS leagues (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                )
            """
            )
            c.execute(
                """ 
                CREATE TABLE IF NOT EXISTS assignors (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                )
            """
            )
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
                )
            """
            )

            conn.commit()
            print("Database rebuilt successfully")
        except sqlite3.Error as e:
            print(f"An error occurred while rebuilding the database: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


# Usage
# rebuild_database(db_file)
