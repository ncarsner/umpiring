# Import necessary classes and functions
from main import Game
import functions

db_file = "officiating.db"

# TSSAA High School game
game = Game(
    # date = "2024-05-12",
    site="Centennial HS",  # Requires site string or select from top 5
    league="tssaa_hs",  # Requires league string or select from top 5
    # assignor=None,  # Get assignor from leagues
    # game_fee=None,
    # fee_paid=False,
    # is_volunteer=False,
)


def main_menu():
    menu_options = {
        "a": lambda: functions.add_game_to_db_v4(db_file, game),
        "u": lambda: functions.update_game_by_id(db_file),
        "v": lambda: functions.review_unpaid_games(db_file),
        "s": lambda: functions.display_season_summary(db_file),
        "d": lambda: functions.database_operations_submenu(),
        "x": lambda: functions.exit_application(),
    }

    while True:
        print()
        print(" Umpiring Revenue and Travel Tracker ".center(45, "*"))
        print("[A]dd Game")
        print("[U]pdate Game")
        print("[V]iew Games")
        print("[S]how Summary")
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


def update_game():
    # Logic to select and update an existing game record
    pass


def database_ops():
    # Logic to update mileage for sites
    pass


if __name__ == "__main__":
    main_menu()
