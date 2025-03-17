from datetime import datetime
import sqlite3
from sqlite3 import Error
from prettytable import PrettyTable
import sys

import googlemaps

from classes import DatabaseHandler
import sites
import leagues

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
            if not game.site or game.site not in sites.ballfields:
                raise ValueError(f"{game.site} not recognized.")
            if not game.league or game.league not in leagues.game_rates:
                raise ValueError(f"{game.league} not recognized")
            # if not game.site or not game.league:
            #     raise ValueError("Site and League required.")

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


def delete_game(db_file):
    """Delete a game by its ID."""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            game_id = input("Enter Game ID to remove: ")
            cursor = conn.cursor()
            # SQL statement to delete a game by ID
            cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Game ID {game_id} deleted successfully.")
            else:
                print(f"No game found with ID {game_id}.")
        except sqlite3.Error as e:
            print(f"An error occurred while trying to delete the game: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


def display_season_summary(db_file):
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cur = conn.cursor()
            current_year = str(datetime.now().year)[-2:]
            sql = f"""
                SELECT league,
                    COUNT(1) as total_games,
                    SUM(CASE WHEN fee_paid = 0 then game_fee else 0 end) as total_owed,
                    SUM(CASE WHEN fee_paid = 1 then game_fee else 0 end) as total_paid,
                    ROUND(SUM(mileage),1) as total_mileage
                FROM games
                WHERE substr(date, 1, 2) = '{current_year}'
                GROUP BY league
            """
            cur.execute(sql)
            summary = cur.fetchall()

            if summary:
                table = PrettyTable()
                table.title = "Season Summary"
                table.field_names = [
                    "League",
                    "Games",
                    "Owed",
                    "Paid",
                    "Mileage",
                ]

                for row in summary:
                    table.add_row(row)

                print(table)
            else:
                print("No data found.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")


def review_all_games(db_file):
    """Function to review unpaid games, with specific fields"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cur = conn.cursor()
            current_year = str(datetime.now().year)[-2:]
            sql = f""" 
                SELECT id, date, site, assignor, game_fee,
                    CASE WHEN fee_paid = 1 then 'Y' else '' end as fee_paid,
                    CASE WHEN is_volunteer = 1 then 'Y' else '' end as is_vol
                FROM games
                WHERE substr(date, 1, 2) = '{current_year}'
            """
            cur.execute(sql)
            all_games = cur.fetchall()

            if all_games:
                table = PrettyTable()
                table.title = "Master Ledger"
                table.field_names = [
                    "ID",
                    "Date",
                    "Site",
                    "Assignor",
                    "Fee",
                    "Paid",
                    "Vol",
                ]

                for game in all_games:
                    table.add_row(game)

                print(table)
            else:
                print("No unpaid games found.")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Error! Cannot create database connection.")


def review_unpaid_games(db_file):
    """Function to review unpaid games, with specific fields"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cur = conn.cursor()
            current_year = str(datetime.now().year)[-2:]
            # Adjusted SQL query to select specific fields
            # sql = """ SELECT g.date, s.name, g.league_id, g.assignor_id, g.game_fee
            #           FROM games g
            #           JOIN sites s ON g.site_id = s.id
            #           WHERE g.fee_paid = 0 """
            sql = f""" 
                SELECT id, date, site, league, assignor, game_fee, fee_paid
                FROM games
                WHERE fee_paid = 0
                AND substr(date, 1, 2) = '{current_year}'
            """
            cur.execute(sql)
            unpaid_games = cur.fetchall()

            if unpaid_games:
                table = PrettyTable()
                table.title = "Unpaid Games"
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
                if field in ["g", "m"]:  # numeric: game_fee, mileage
                    new_value = float(new_value)
                if field in ["f", "v"]:  # boolean: fee_paid, is_volunteer
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


def bulk_update_games_paid_status(db_handler):
    unpaid_game_ids = db_handler.fetch_unpaid_game_ids()
    if not unpaid_game_ids:
        print("There are no unpaid games to update.")
        return

    print("Game IDs: ", unpaid_game_ids)
    user_input = input("Enter game IDs to mark as paid (comma-separated): ")

    # Split the input and convert to integers
    try:
        game_ids = [int(id.strip()) for id in user_input.split(",")]
    except ValueError:
        print("Invalid input. Please enter valid game IDs.")
        return

    # Validate that all entered IDs are unpaid game IDs
    if not all(game_id in unpaid_game_ids for game_id in game_ids):
        print("Invalid game IDs. Enter only unpaid game IDs.")
        return

    # Confirm update
    confirmation = input("Confirm mark as paid? ").lower()
    if confirmation in ["yes", "y", 1]:
        db_handler.bulk_update_games_paid_status(game_ids, True)
        print(f"Games {game_ids} marked as paid.")
    else:
        print("Operation canceled.")


def database_operations_submenu():
    db_operations = {
        "x": return_to_main_menu,
        "d": db_handler.drop_tables,
        "c": db_handler.create_games_table,
        "m": db_handler.create_relation_tables,
        "re": db_handler.rebuild_database,
    }

    while True:
        print(" Database Operations ".center(45, "*"))
        print("E[x]it to Main Menu")
        print("[D]rop tables")
        print("[C]reate games table")
        print("[M]ake relational tables")
        print("[RE]initialize database\n")
        choice = input("Enter your choice: ").lower()

        if choice == "x":
            break
        elif choice in db_operations:
            confirmation = input("Are you sure?? ").lower()
            if confirmation in ["yes", "y"]:
                db_operations[choice]()
        else:
            print("Invalid choice. Please try again.")


def return_to_main_menu():
    # breaks database_operations_submenu loop to return to main
    pass


# Gets distances using Google Maps API for a dictionary of addresses
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


def update_zero_mileage_entries(api_key, default_from, db_handler):
    gmaps = googlemaps.Client(key=api_key)
    zero_mileage_sites = db_handler.fetch_sites_with_zero_mileage()

    if not zero_mileage_sites:
        print("No sites with zero mileage found.")
        return

    for site_name, address in zero_mileage_sites.items():
        distance_result = gmaps.distance_matrix(default_from, address, mode="driving")
        if distance_result["rows"][0]["elements"][0]["status"] == "OK":
            distance_text = distance_result["rows"][0]["elements"][0]["distance"][
                "text"
            ]
            if "km" in distance_text:
                distance_km = float(distance_text.split()[0].replace(",", ""))
                distance_miles = round(distance_km * 0.621371, 1)
            else:
                distance_miles = float(
                    distance_text.split()[0]
                )  # Assuming miles directly if not km

            db_handler.save_mileage_for_site(site_name, distance_miles)
            print(f"Updated {site_name} with {distance_miles} miles.")
        else:
            print(f"Could not update {site_name}. Distance not found.")


def calculate_and_cache_distances(
    api_key, default_from, ballfields, db_handler=db_handler
):
    gmaps = googlemaps.Client(key=api_key)
    distances = {}

    for site_name, address in ballfields.items():
        # Check if mileage is already cached in the database
        cached_mileage = db_handler.get_mileage_for_site(site_name)
        if cached_mileage is not None:
            distances[site_name] = f"{cached_mileage} miles"
            continue

        # API call for sites not cached
        distance_result = gmaps.distance_matrix(default_from, address, mode="driving")
        if distance_result["rows"][0]["elements"][0]["status"] == "OK":
            distance_text = distance_result["rows"][0]["elements"][0]["distance"][
                "text"
            ]
            if "km" in distance_text:
                distance_km = float(distance_text.split()[0].replace(",", ""))
                distance_miles = round(distance_km * 0.621371, 1)
            else:
                distance_miles = float(
                    distance_text.split()[0]
                )  # Assuming miles directly if not km

            distances[site_name] = f"{distance_miles} miles"
            db_handler.save_mileage_for_site(site_name, distance_miles)
        else:
            distances[site_name] = "Distance not found"

    return distances
