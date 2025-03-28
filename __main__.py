# Import necessary
from classes import Game, DatabaseHandler
import functions
import random
import leagues
import sites
from datetime import date, timedelta
import configparser

# Database setup
config = configparser.ConfigParser()
config.read("config.ini")
API_KEY = config["credentials"]["api_key"]
DEFAULT_FROM = config["credentials"]["default_from"]

db_file = "officiating.db"
db_handler = DatabaseHandler(db_file)

random_date = date.today() + timedelta(days=random.randint(1, 120))
random_site = random.choice(list(sites.ballfields.keys()))
random_league = random.choice(list(leagues.game_rates.keys()))

# Instance of the Game class
game = Game(
    date=random_date.strftime("%y%m%d"),
    site=random_site,
    league=random_league,
    # assignor=None,  # Get assignor from leagues
    # game_fee=None, # Get game fee from leagues
    # fee_paid=False, # default=False
    # is_volunteer=False, # default=False
    db_handler=db_handler,
)


def main_menu():
    menu_options = {
        "a": lambda: functions.add_game_to_db(db_file, game),
        "u": lambda: functions.update_game_by_id(db_file),
        "r": lambda: functions.delete_game(db_file),
        "v": lambda: functions.review_unpaid_games(db_file),
        "b": lambda: functions.bulk_update_games_paid_status(DatabaseHandler(db_file)),
        "g": lambda: functions.review_all_games(db_file),
        "s": lambda: functions.display_season_summary(db_file),
        "d": lambda: functions.database_operations_submenu(),
        "x": lambda: functions.exit_application(),
    }

    while True:
        print()
        print(" Umpiring Revenue and Travel Tracker ".center(45, "*"))
        print("[A]dd Game")
        print("[U]pdate Game")
        print("[R]emove Game")
        print("[V]iew Unpaid Games")
        print("[B]ulk Paid Games")
        print("[G]ame Ledger")
        print("[S]eason Summary")
        print("[D]atabase Ops")
        print("E[x]it\n")
        choice = input("Enter your choice: ").lower()

        if choice in menu_options:
            menu_options[choice]()
        elif choice == "x":
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
