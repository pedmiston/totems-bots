from bots.models import create_team

def test_create_team():
    team = create_team()
    assert len(team.players) == 1

def test_players_recreate_team_items():
    team = create_team()
    team.active_players = team.players
    team.inventory = [1, 2, 3, 4, 5, 6, 23]
    guess = team.make_guesses()[1]
    assert set(guess) == set([3, 6])
