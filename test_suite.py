from main import Game  # Assuming your Game class is in game.py

def test_game_creation_with_defaults():
    game = Game(date="2021-01-01", site="Central Park", league="Big League", assignor="John Doe", game_fee=100)
    assert game.date == "2021-01-01"
    assert game.site == "Central Park"
    assert game.league == "Big League"
    assert not game.assignor == "John Doe"
    assert game.game_fee == 100
    assert not game.fee_paid
    assert not game.is_volunteer
    assert game.mileage == 0.0

def test_game_creation_with_all_params():
    game = Game(date="2021-01-01", site="Central Park", league="Big League", assignor="John Doe", game_fee=100, fee_paid=True, is_volunteer=True, mileage=15.5)
    assert game.date == "2021-01-01"
    assert game.site == "Central Park"
    assert game.league == "Big League"
    assert not game.assignor == "John Doe"
    assert game.game_fee == 100
    assert game.fee_paid
    assert game.is_volunteer
    assert game.mileage == 15.5

# Additional test cases as needed
