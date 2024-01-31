import sqlite3
from sqlite3 import Error
from prettytable import PrettyTable
import sys
from classes import DatabaseHandler

import googlemaps

db_file = "officiating.db"
db_handler = DatabaseHandler(db_file)


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


def exit_application():
    print("Exiting the application.")
    sys.exit()


def add_game_to_db(db_file, game):
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
                SELECT id, date, site, league, assignor, game_fee, fee_paid
                FROM games
                WHERE fee_paid = 0
            """
            cur.execute(sql)
            unpaid_games = cur.fetchall()

            if unpaid_games:
                table = PrettyTable()
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
                if field in ["g", "m"]:  # Assuming game_fee, mileage are numeric
                    new_value = float(new_value)
                if field in [
                    "f",
                    "v",
                ]:  # Assuming fee_paid, is_volunteer are bool
                    new_value = new_value.lower() in ["yes", "y", "true", "1"]

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
        "x": return_to_main_menu,
        "d": db_handler.drop_tables,
        "c": db_handler.create_games_table,
        "m": db_handler.create_relation_tables,
        "re": db_handler.initialize_database,
    }

    while True:
        print("\nDatabase Operations")
        print("E[x]it to Main Menu")
        print("[D]rop tables")
        print("[C]reate games table")
        print("[M]ake relational tables")
        print("[RE]initialize database\n")
        choice = input("Enter your choice: ").lower()

        if choice == "x":
            break
        elif choice in db_operations:
            confirmation = input("Are you sure?? (yes/no) ").lower()
            if confirmation in ["yes", "y"]:
                db_operations[choice]()
        else:
            print("Invalid choice. Please try again.")


def return_to_main_menu():
    # This function simply breaks the loop in the database_operations_submenu
    # to return to the main menu.
    pass


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


# def get_sites_with_zero_mileage(db_file):
#     """Retrieve sites with 0 mileage from the database"""
#     conn = create_connection(db_file)
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT name FROM sites WHERE mileage = 0")
#         sites = cur.fetchall()
#         return [site[0] for site in sites]
#     except sqlite3.Error as e:
#         print(e)
#     finally:
#         conn.close()
#     return []


# def update_zero_mileage_sites(db_file, api_key, default_from):
#     """Update sites with 0 mileage using Google Maps API"""
#     sites = get_sites_with_zero_mileage(db_file)
#     if sites:
#         destination_addresses = {
#             site: site for site in sites
#         }  # Assuming site name is the address
#         distances = calculate_distances(api_key, default_from, destination_addresses)

#         for site, distance in distances.items():
#             if "miles" in distance:
#                 mileage = float(distance.split()[0])
#                 update_site_mileage(db_file, site, mileage)
#                 print(f"Updated mileage for {site}: {mileage} miles")
#             else:
#                 print(f"Distance not found for {site}")
