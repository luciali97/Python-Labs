#!/usr/bin/env python3
import os
import lab
import json
import unittest
import doctest
import importlib, importlib.util
from copy import deepcopy

TEST_DIRECTORY = os.path.dirname(__file__)

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
TESTDOC_SKIP = ["lab"]


class TestDocTests(unittest.TestCase):
    def test_doctests_run(self):
        """ Checking to see if all lab doctests run successfully """
        results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
        self.assertEqual(results[0], 0)

    def test_all_doc_strings_exist(self):
        """ Checking if docstrings have been written for everything in lab.py """
        tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
        for test in tests:
            if test.name in TESTDOC_SKIP:
                continue
            if not test.docstring:
                missing = "Oh no, '{}' has no docstring!".format(test.name)
                self.fail(missing)


class TestNewGame(unittest.TestCase):
    def test_newsmallgame(self):
        """ Testing new_game on a small board """
        result = lab.MinesGame(10, 8, [(7, 3), (2, 6), (8, 7), (4, 4), (3, 5),
                                      (4, 6), (6, 2), (9, 4), (4, 2), (4, 0),
                                      (8, 6), (9, 7), (8, 5), (5, 0), (7, 2),
                                      (5, 3)])
        expected = {"board": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 1, 1, 1],
                              [0, 0, 0, 0, 1, 2, ".", 1],
                              [1, 2, 1, 2, 2, ".", 3, 2],
                              [".", 3, ".", 3, ".", 3, ".", 1],
                              [".", 4, 3, ".", 2, 2, 1, 1],
                              [1, 3, ".", 4, 2, 0, 0, 0],
                              [0, 2, ".", ".", 2, 2, 3, 2],
                              [0, 1, 2, 3, 3, ".", ".", "."],
                              [0, 0, 0, 1, ".", 3, 4, "."]],
                    "dimensions": [10, 8],
                    "mask": [[False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False]],
                    "state": "ongoing"}
        for name in expected:
            self.assertEqual(getattr(result, name), expected[name])

    def test_newmediumgame(self):
        """ Testing new_game on a medium board """
        result = lab.MinesGame(30, 16, [(16, 6), (17, 7), (14, 4), (13, 4),
                                       (0, 7), (21, 6), (2, 5), (5, 5), (6, 10),
                                       (12, 6), (24, 14), (14, 1), (24, 1),
                                       (26, 12), (8, 15), (9, 3), (16, 0),
                                       (19, 13), (15, 14), (13, 10), (18, 10),
                                       (21, 15), (28, 15), (29, 14), (11, 15),
                                       (14, 8), (17, 8), (24, 8), (25, 5),
                                       (2, 1), (10, 3), (27, 2), (17, 6),
                                       (7, 15), (15, 0), (21, 8), (20, 0),
                                       (1, 10), (10, 4), (14, 6), (1, 0),
                                       (4, 11), (27, 0), (9, 13), (23, 5),
                                       (14, 12), (20, 15), (3, 15), (26, 14),
                                       (4, 8), (10, 15), (7, 11), (18, 1),
                                       (25, 4), (26, 3), (22, 14), (28, 2),
                                       (13, 2), (19, 6), (1, 4), (21, 4),
                                       (1, 9), (8, 7), (23, 1), (22, 11),
                                       (19, 5), (18, 7), (0, 6), (26, 4),
                                       (3, 4), (5, 9), (24, 13), (20, 8),
                                       (19, 0), (0, 3), (21, 13), (3, 3),
                                       (28, 9), (11, 1), (12, 10), (24, 10),
                                       (18, 13), (0, 0), (21, 0), (3, 13),
                                       (27, 13), (5, 15), (26, 9), (17, 4),
                                       (7, 9), (19, 9), (24, 7), (22, 5),
                                       (3, 8), (27, 8), (9, 5), (23, 13),
                                       (5, 2), (10, 2)])
        with open("test_outputs/test_newmediumgame.json") as f:
            expected = json.load(f)
        for name in expected:
            self.assertEqual(getattr(result, name), expected[name])


    def test_newlargegame(self):
        """ Testing new_game on a medium board """
        with open("test_outputs/test_newlargegame.json") as f:
            expected = json.load(f)
        with open("test_inputs/test_newlargegame.json") as f:
            inputs = json.load(f)
        result = lab.MinesGame(inputs["num_rows"], inputs["num_cols"],
                               inputs["bombs"])
        for name in expected:
            self.assertEqual(getattr(result, name), expected[name])


class TestDig(unittest.TestCase):
    def test_dig(self):
        for t in ('mine', 'small','complete'):
            with self.subTest(test=t):
                with open("test_outputs/test_dig%s.json" % t) as f:
                    expected = json.load(f)
                with open("test_inputs/test_dig%s.json" % t) as f:
                    inputs = json.load(f)
                game = game_from_dict(inputs["game"])
                revealed = game.dig(inputs['row'], inputs['col'])
                self.assertEqual(revealed, expected['revealed'])
                for name in expected['game']:
                    self.assertEqual(getattr(game, name), expected['game'][name])


class TestRender(unittest.TestCase):
    def test_render(self):
        """ Testing render on a small board """
        with open("test_inputs/test_render.json") as f:
            inp = json.load(f)
        result = game_from_dict(inp).render()
        expected = [[" ", " ", " ", " ", " ", " ", " ", " "],
                    [" ", " ", " ", " ", " ", "1", "1", "1"],
                    [" ", " ", " ", " ", "1", "2", "_", "_"],
                    ["1", "2", "1", "2", "2", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_", "_"]]
        self.assertEqual(result, expected)

class TestRenderAscii(unittest.TestCase):
    def test_asciismall(self):
        """ Testing render_ascii on a small 2d board """
        with open("test_inputs/test_asciismall.json") as f:
            inp = json.load(f)
        result = game_from_dict(inp).render_ascii()
        expected = ("        \n"
                    "     111\n"
                    "    12__\n"
                    "12122___\n"
                    "________\n"
                    "________\n"
                    "________\n"
                    "________\n"
                    "________\n"
                    "________")
        self.assertEqual(result, expected)

    def test_asciixray(self):
        """ Testing render_ascii on a small 2d board with xray """
        with open("test_inputs/test_asciixray.json") as f:
            inputs = json.load(f)
        result = game_from_dict(inputs['game']).render_ascii(True)
        expected = ("        \n"
                    "     111\n"
                    "    12.1\n"
                    "12122.32\n"
                    ".3.3.3.1\n"
                    ".43.2211\n"
                    "13.42   \n"
                    " 2..2232\n"
                    " 1233...\n"
                    "   1.34.")
        self.assertEqual(result, expected)


class TestIntegration(unittest.TestCase):
    def run_integration_test(self, t):
        """ dig, render, and render_ascii on boards """
        with open("test_outputs/test_integration%d.json" % t) as f:
            expected = json.load(f)
        with open("test_inputs/test_integration%s.json" % t) as f:
            inputs = json.load(f)
        results = []
        game = game_from_dict(inputs['game'])
        for coord in inputs['coords']:
            results.append([["dig", game.dig(*coord)],
                            ["board", dict_from_game(game)],
                            ["render", game.render()],
                            ["render/xray", game.render(True)],
                            ["render_ascii", game.render_ascii()],
                            ["render_ascii/xray", game.render_ascii(True)]])
        self.assertEqual(results, expected)

    def test_integration_1(self):
        self.run_integration_test(1)

    def test_integration_2(self):
        self.run_integration_test(2)

    def test_integration_3(self):
        self.run_integration_test(3)


class TestNewTests(unittest.TestCase):
    def test_init_board(self):
        g = lab.MinesGame(5,5,[(0,3),(2,0),(3,0),(3,3)])
        results = g.board
        expected = [[0, 0, 1, '.', 1], [1, 1, 1, 1, 1], ['.', 2, 1, 1, 1], ['.', 2, 1, '.', 1], [1, 1, 1, 1, 1]]
        self.assertEqual(results, expected)
    
    def test_victory_1(self):
        """
        if the state is victory before we dig, then it should return 0 instead of 1
        """
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "victory",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, True, True],
                                              [False, True, True],
                                             [True, True, True]]})
        results = g.dig(1,1)
        expected = 0
        self.assertEqual(results, expected)
        
    def test_dig_nonzero(self):
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "ongoing",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, False, True],
                                              [False, False, True],
                                             [True, True, True]]})
        results = g.dig(1,1)
        expected = 1
        self.assertEqual(results, expected)
    
    def test_dig_zero(self):
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "ongoing",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, False, False],
                                              [False, False, False],
                                             [True, True, False]]})
        results = g.dig(0,2)
        expected = 5
        self.assertEqual(results, expected)
        
    def test_dig_victory(self):
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "ongoing",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, True, True],
                                              [False, True, True],
                                             [False, True, True]]})
        results = g.dig(2,0)
        expected = 1
        self.assertEqual(results, expected)
        
    def test_height_width(self):
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "ongoing",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, False, False],
                                              [False, False, False],
                                             [False, False, False]]})
        results = g.dig(1,1)
        expected = 1
        self.assertEqual(results, expected)
    
    def test_cooef(self):
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "ongoing",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, False, False],
                                              [False, False, False],
                                             [False, False, False]]})
        results = g.dig(2,0)
        expected = 1
        self.assertEqual(results, expected)
    
    def test_mask(self):
        g = lab.MinesGame.from_dict({"dimensions": [3, 3],
                                    "state": "ongoing",
                                    "board": [[".", 2,0], [".",2,0], [1,1,0]],
                                    "mask":  [[False, False, False],
                                              [False, False, False],
                                             [False, False, False]]})
        results = g.dig(2,1)
        expected = 1
        self.assertEqual(results, expected)

def game_from_dict(d):
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
    game = lab.MinesGame(r, c, bombs)
    for i in ('board', 'state', 'mask'):
        setattr(game, i, d[i])
    return game


def dict_from_game(g):
    return {k: deepcopy(getattr(g, k)) for k in ('dimensions', 'board', 'state', 'mask')}

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
