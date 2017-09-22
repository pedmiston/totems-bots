from sys import stdout
from itertools import product
from collections import namedtuple

import yaml
import json
import pandas

from graph import Landscape

from .models import create_team
from .strategies import strategies
from .util import get_as_list, jsonify_new_items


"""An instance of SimVars contains the parameters for running a simulation.

The order of the fields in SimVars must match the call signature for the
"simulate" function. Also, all SimVars fields must be available as properties
of the Experiment class.
"""
SimVars = namedtuple('SimVars',
    'strategy n_guesses n_players seed player_memory team_memory')
RoundVars = namedtuple('RoundVars',
    'guesses new_items inventory inventory_size trajectory n_team_guesses n_player_unique_guesses n_team_unique_guesses')


def simulate(strategy, n_guesses, n_players, seed, player_memory, team_memory):
    landscape = Landscape()
    team = create_team(n_players, player_memory=player_memory,
                       team_memory=team_memory)
    rounds = []

    # Keep track of player and team memories outside of
    # player and team models to monitor unique guesses.
    player_memories = {player_id+1: []
                       for player_id, _ in enumerate(team.players)}
    team_memories = []

    for iteration in strategy(team, n_guesses):
        guesses = team.make_guesses()
        new_items = landscape.evaluate_guesses(guesses.values())
        if len(new_items) > 0:
            team.update_inventory(new_items)

        # Record total guesses and guess uniqueness for players and team
        n_team_guesses = len(guesses.values())
        n_player_unique_guesses = 0
        n_team_unique_guesses = 0
        for player_id, guess in guesses.items():
            if guess not in player_memories[player_id]:
                n_player_unique_guesses += 1
                player_memories[player_id].append(guess)

            if guess not in team_memories:
                n_team_unique_guesses += 1
                team_memories.append(guess)

        rounds.append(dict(
            strategy=strategy.__name__,
            n_guesses=n_guesses,
            n_players=n_players,
            seed=seed,
            player_memory=int(player_memory),
            team_memory=int(team_memory),
            round=iteration,
            guesses=guesses,
            new_items=jsonify_new_items(new_items),
            inventory=json.dumps(list(team.inventory)),
            inventory_size=len(team.inventory),
            trajectory=team.trajectory,
            n_team_guesses = n_team_guesses,
            n_player_unique_guesses=n_player_unique_guesses,
            n_team_unique_guesses=n_team_unique_guesses,
        ))

        if len(team.inventory) == landscape.max_items:
            break

    output_cols = SimVars._fields + ('round', ) + RoundVars._fields
    results = pandas.DataFrame.from_records(rounds, columns=output_cols)
    return results


def run_experiment(experiment_yaml, output=None, verbose=False):
    """Run an experiment, which is a collection of simulations."""
    experiment = read_experiment_yaml(experiment_yaml)
    output = open(output, 'w') if output else stdout
    for sim_id, sim_vars in enumerate(experiment.simulations()):
        if verbose:
            # Replace strategy which is a function with the name of the function
            strategy_ix = SimVars._fields.index('strategy')
            pretty_sim_vars = sim_vars[:strategy_ix] + \
                              (sim_vars[strategy_ix].__name__, ) + \
                              sim_vars[strategy_ix+1:]
            print(' #{}: {}'.format(sim_id, SimVars(*pretty_sim_vars)))
        results = simulate(*sim_vars)
        results.insert(0, 'sim_id', sim_id)
        first_write = (sim_id == 0)
        results.to_csv(output, index=False, header=first_write, mode='a')
    output.close()


def read_experiment_yaml(experiment_yaml):
    return Experiment.from_yaml(experiment_yaml)


class Experiment:
    """A group of simulations created from experimental variables."""
    def __init__(self, data=None):
        self._data = data or dict()

    @classmethod
    def from_yaml(cls, experiment_yaml):
        data = yaml.load(open(experiment_yaml))
        return cls(data)

    def simulations(self):
        """Yield the product of experiment variables."""
        props = [getattr(self, prop) for prop in SimVars._fields]
        return product(*props)

    def expand_all(self):
        return pandas.DataFrame(list(self.simulations()),
                                columns=SimVars._fields)

    def get_as_list(self, key, default=None):
        return get_as_list(self._data, key, default)

    # ---- Start of experiment variables as object properties ----

    @property
    def strategy(self):
        """A list of strategies."""
        names = self.get_as_list('strategy')
        return [strategies[name] for name in names]

    @property
    def n_guesses(self):
        """A list of guess amounts to be allotted to teams."""
        return self.get_as_list('n_guesses')

    @property
    def n_players(self):
        return self.get_as_list('n_players')

    @property
    def seed(self):
        """A list of seeds to use when initializing the teams."""
        return range(self._data['n_seeds'])

    @property
    def player_memory(self):
        return self.get_as_list('player_memory', False)

    @property
    def team_memory(self):
        return self.get_as_list('team_memory', True)
