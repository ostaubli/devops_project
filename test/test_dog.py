# This is the test file for the whole dog.py file
# The test file should be in the test folder and called test_dog.py for benchmark_dog.py to find it

# Write your test functions in this file, that is clear and easy to understand what you are testing

##################################################
# Run with: python test/test_dog.py python dog.Dog
##################################################

import os
import sys
import abc
import benchmark
import importlib
import json
import traceback

from pydantic import BaseModel
from typing import List, Optional, Dict

from server.py.dog import Card, Marble, PlayerState, Action, GameState, GamePhase

from benchmark.benchmark import Benchmark

#class DogBenchmark(benchmark.Benchmark): # This is how its called by benchmark_dog.py
class DogBenchmark(Benchmark): # if it doesnt work, comment out and try the above line

    CNT_PLAYERS = 4
    CNT_STEPS = 64
    CNT_BALLS = 4

    # --- tests ---

    def test_test(self):
        """Test 001: Validate values of initial game state [1 points]"""
        assert True



    # --- end of tests ---

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Error: Wrong number of arguments")
        print("Use: python benchmark_dog_copy.py python [dog.Dog]")
        print("  or python benchmark_dog_copy.py localhost [port]")
        print("  or python benchmark_dog_copy.py remote [host:port]")
        sys.exit()

    benchmark = DogBenchmark(argv=sys.argv)
    benchmark.run_tests()
