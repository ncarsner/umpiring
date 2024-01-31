import pytest
import sqlite3
from classes import Game, DatabaseHandler

# Configuring a test database
TEST_DB = "test_officiating.db"


def test_game_creation_with_defaults():
    game = Game(
        date="2021-01-01",
        site="Central Park",
        league="Big League",
        assignor="John Doe",
        game_fee=100,
    )
    assert game.date == "2021-01-01"
    assert game.site == "Central Park"
    assert game.league == "Big League"
    assert not game.assignor == "John Doe"
    assert not game.game_fee == 100
    assert not game.fee_paid
    assert not game.is_volunteer
    assert game.mileage == 0.0


def test_game_creation_with_all_params():
    game = Game(
        date="2021-01-01",
        site="Central Park",
        league="Big League",
        assignor="John Doe",
        game_fee=100,
        fee_paid=True,
        is_volunteer=True,
        mileage=15.5,
    )
    assert game.date == "2021-01-01"
    assert game.site == "Central Park"
    assert game.league == "Big League"
    assert not game.assignor == "John Doe"
    assert game.game_fee == 100
    assert game.fee_paid
    assert game.is_volunteer
    assert game.mileage == 15.5


@pytest.fixture
def db_handler():
    """Fixture to create a DatabaseHandler instance for tests."""
    return DatabaseHandler(TEST_DB)


@pytest.fixture
def setup_test_db(db_handler):
    """Fixture to set up the test database."""
    db_handler.rebuild_database()  # Assuming this method resets the DB


def test_create_table(db_handler, setup_test_db):
    """Test creating tables in the database."""
    # Assuming create_table method creates a specific table, e.g., 'games'
    db_handler.create_table()
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games';")
    table_exists = cur.fetchone()
    conn.close()
    assert table_exists is not None


def test_rebuild_database(db_handler):
    """Test rebuilding the database."""
    db_handler.rebuild_database()
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    conn.close()
    # Assuming there are specific tables to check for
    assert ("games",) in tables
    # Add more assertions for other tables


def test_add_game(db_handler, setup_test_db):
    """Test adding a game to the database."""
    test_game_data = {
        "date": "2023-01-01",
        "site": "Test Park",
        "league": "Test League",
        "assignor": "John Tester",
        "game_fee": 100,
        # Include other fields as necessary
    }
    db_handler.add_game(test_game_data)  # Adjust this based on your implementation
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE site = 'Test Park';")
    game = cur.fetchone()
    conn.close()
    assert game is not None
    assert game[1] == "Test Park"  # Adjust index based on your table structure
