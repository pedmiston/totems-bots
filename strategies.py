def synchronic(team, n_guesses):
    """Activate all of the team's players.

    Spends labor hours in the fastest way possible.
    """
    team.active_players = team.players
    calendar_hours = int(n_guesses/len(team.players))
    for calendar_hour in range(calendar_hours):
        yield calendar_hour


def diachronic(team, n_guesses):
    """Activate one of the team's players at a time.

    Spends calendar hours in the slowest way possible.
    """
    hours_per_player = int(n_guesses/len(team.players))
    ix = 0  # start with first player in the team
    for calendar_hour in range(n_guesses):
        if calendar_hour % hours_per_player == 0:
            team.active_players = [team.players[ix]]
            ix = (ix + 1) % len(team.players)
        yield calendar_hour


def full(team, n_guesses):
    """Activate all of the team's players and give them extra time.

    This strategy is used to replicate the conditions of Derex & Boyd (2015).
    """
    team.active_players = team.players
    for calendar_hour in range(n_guesses):
        yield calendar_hour


def solo(team, n_guesses):
    """The first player in the team plays the whole round."""
    team.active_players = [team.players[0]]
    for calendar_hour in range(n_guesses):
        yield calendar_hour


strategies = dict(
    synchronic=synchronic,
    diachronic=diachronic,
    full=full,
    solo=solo,
)
