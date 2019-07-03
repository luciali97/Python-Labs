import os
import doctest
import time
import traceback

import importlib, importlib.util
from copy import deepcopy
from collections import OrderedDict

# programmatically import buggy implementations

try:
    import lab
    importlib.reload(lab)
except ImportError:
    import solution
    lab = solution

# list different implementations
# called by ui
def list_impls(d):
    return ["lab"]

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
def testdoc(target):
    if target == "lab":
        results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
    elif target == "readme":
        results = doctest.testfile("readme.md", optionflags=TESTDOC_FLAGS, report=False)
    return results[0] == 0

def checkdoc(kind):
    tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
    for test in tests:
        if test.name == "lab":
            continue
        if kind == "docstrings" and not test.docstring:
            return "Oh no, '{}' has no docstring!".format(test.name)
        if kind == "doctests" and not test.examples:
            return "Oh no, '{}' has no doctests!".format(test.name)
    return {"docstrings": "All functions are documented; great!",
            "doctests": "All functions have tests; great!"}[kind]

def dict_from_game(g):
    return {k: deepcopy(getattr(g, k)) for k in ('dimensions', 'board', 'state', 'mask')}

def game_from_dict(cls, d):
    """
    Create an instance of `lab.MinesGame` from a dictionary representation of
    the game.
    """
    r, c = d['dimensions']
    bombs = []
    for i in range(r):
        for j in range(c):
            if d['board'][i][j] == '.':
                bombs.append((i, j))
    game = cls(r, c, bombs)
    for i in ('board', 'state', 'mask'):
        setattr(game, i, d[i])
    return game

def get_impl(d):
    return lab

def ui_new_game(d):
    return dict_from_game(get_impl(d).MinesGame(d["num_rows"], d["num_cols"], d["bombs"]))

def ui_dig(d):
    game, row, col = d["game"], d["row"], d["col"]
    game = game_from_dict(get_impl(d).MinesGame, d['game'])
    nb_dug = game.dig(row, col)
    status = game.state
    return [dict_from_game(game), status, nb_dug]

def ui_render(d):
    g = d['game']
    x = d['xray']
    b = g['board']
    m = g['mask']
    r = d['our_renderer']
    if r:
        return [[ '_' if (not x) and (not m[r][c]) else ' ' if b[r][c] == 0 else str(b[r][c]) for c in range(d['num_cols'])] for r in range(d['num_rows'])]
    else:
        try:
            game = game_from_dict(get_impl(d).MinesGame, d['game'])
            r = game.render(x)
        except:
            r = [['ERROR' for i in range(d['num_cols'])] for j in range(d['num_rows'])]
        return r
