#!/usr/bin/env python3
import os
import lab
import time
import pickle
import unittest
import sys
import warnings
sys.setrecursionlimit(10000)

TEST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'test_files')
with open(os.path.join(TEST_DIRECTORY, 'results'), 'rb') as f:
        RESULTS = pickle.load(f)

class Lab9Test(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

class Test1_Streaming(Lab9Test):
    def test_streaming(self):
        t = time.time()
        x1, x2 = RESULTS['test_streaming']
        stream = lab.download_file('http://scripts.mit.edu/~6.009/lab9/test_stream.py')
        self.assertEqual(next(stream), x1)
        self.assertEqual(next(stream), x2)
        self.assertTrue((time.time()-t) < 30, msg="Download took too long.")


class Test2_Behaviors(Lab9Test):
    def test_redirect(self):
        stream = lab.download_file('http://scripts.mit.edu/~6.009/lab9/redir.py/0/fivedollars.wav')
        self.assertEqual(b''.join(stream), RESULTS['test_redirect'])

        with self.assertRaises(RuntimeError):
            stream = lab.download_file('http://scripts.mit.edu/~6.009/lab9/always_error.py/')
            out = b''.join(stream)
        with self.assertRaises(RuntimeError):
            stream = lab.download_file('http://nonexistent.mit.edu/hello.txt')
            out = b''.join(stream)
        with self.assertRaises(FileNotFoundError):
            stream = lab.download_file('http://hz.mit.edu/some_file_that_doesnt_exist.txt')
            out = b''.join(stream)


class Test3_Manifest(Lab9Test):
    def test_big(self):
        stream = lab.download_file('http://scripts.mit.edu/~6.009/lab9/redir.py/0/cat_poster.jpg.parts')
        self.assertEqual(b''.join(stream), b''.join(RESULTS['test_big']))


class Test4_Caching(Lab9Test):
    def test_cache(self):
        # test that cache hits speed things up
        t = time.time()
        stream = lab.download_file('http://mit.edu/6.009/www/lab9_examples/happycat.png.parts')
        result = b''.join(stream)
        expected = 10*RESULTS['test_caching.1']
        self.assertEqual(result, expected)
        self.assertTrue(time.time() - t < 15, msg='Test took too long.')

        # test that caching isn't done unnecessarily (only where specified)
        stream = lab.download_file('http://mit.edu/6.009/www/lab9_examples/numbers.png.parts')
        result = b''.join(stream)
        count = sum(i in result for i in RESULTS['test_caching.2'])
        self.assertTrue(count > 1)



def _test_5_gen():
    with open(os.path.join(TEST_DIRECTORY, 'test_file_sequence.input'), 'rb') as f:
        inp = f.read()
    for i in range(0, len(inp), 8192):
        yield inp[i:i+8192]
        if i == 270336:
            time.sleep(5)
    yield inp[i+8192:]


class Test5_Sequence(Lab9Test):
    def test_file_sequence(self):
        gen = _test_5_gen()
        t = time.time()
        for ix, file_ in enumerate(lab.files_from_sequence(gen)):
            self.assertEqual(file_, RESULTS['test_file_sequence'][ix],
                             msg='File %d in the sequence was not correctly extracted.' % ix)
            if ix == 4:
                self.assertTrue(time.time() - t < 0.5, msg="Yielding first 5 files took too long")

        self.assertEqual(ix, len(RESULTS['test_file_sequence'])-1,
                         msg='Incorrect number of files in file sequence.')


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
