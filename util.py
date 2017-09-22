import json

import numpy


def get_as_list(data, key, default=None):
    result = data.get(key, default)
    if not isinstance(result, list):
        result = [result]
    return result


def jsonify_new_items(new_items):
    """Convert a dict of frozenset keys and item label values to json data.

    Returns a list of json objects:

        [
            {'guess': ['item'], 'result': 'item'}
        ]
    """
    results = []
    for guess, result in new_items.items():
        guess = list(guess)
        if isinstance(guess[0], numpy.int64):
            guess = list(map(int, guess))
            result = int(result)

        results.append({'guess': guess, 'result': result})
    return json.dumps(results)
