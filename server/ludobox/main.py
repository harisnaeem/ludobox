#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 3 compatibility
from __future__ import print_function

import os
import glob
import shutil
import argparse
import py
import sys

from ludobox.run import serve

# TODO: move this to config file
INPUT_DIR = os.path.join(os.getcwd(),"data")
OUTPUT_DIR = os.path.join(os.getcwd(),"static")

def clean(**kwargs):
    """Delete tmp files

    This function will remove:
    *   any *.pyc file generated by previous python execution/test
    *   any *.pyo file generated by previous python execution/test
    *   any __pycache__ files generated by previous python :mod:`py.test`

    """

    print("Remove all precompiled python files (*.pyc): ", end='')
    for f in glob.glob("server/**/*.pyc"):
        os.remove(f)
    print("SUCCESS")

    print("Remove all python generated object files (*.pyo): ", end='')
    for f in glob.glob("server/**/*.pyo"):
        os.remove(f)
    print("SUCCESS")

    print("Remove py.test caches directory (__pycache__): ", end='')
    shutil.rmtree("__pycache__", ignore_errors=True)
    shutil.rmtree("server/tests/__pycache__", ignore_errors=True)
    print("SUCCESS")

def test(fulltrace, **kwargs):
    """Run tests from the command line"""

    # unexported constasts used as pytest.main return codes
    # c.f. https://github.com/pytest-dev/pytest/blob/master/_pytest/main.py
    PYTEST_EXIT_OK = 0
    PYTEST_EXIT_TESTSFAILED = 1
    PYTEST_EXIT_INTERRUPTED = 2
    PYTEST_EXIT_INTERNALERROR = 3
    PYTEST_EXIT_USAGEERROR = 4
    PYTEST_EXIT_NOTESTSCOLLECTED = 5

    cmd = "server/tests"

    if fulltrace : cmd = cmd + " --fulltrace"

    unit_result = py.test.cmdline.main(cmd)
    # return the right code
    if unit_result not in (PYTEST_EXIT_OK, PYTEST_EXIT_NOTESTSCOLLECTED):
        print("To have more details about the errors you should try the command: py.test tests", file=sys.stderr)
        sys.exit("TESTS : FAIL")
    else:
        print("TESTS : SUCCESS")


# TODO add an info action that list the default dirs, all actual games
#   installed
def parse_args(args):
    """Configure the argument parser and returns it."""
    # Initialise the parsers
    parser = argparse.ArgumentParser(description="Ludobox server.")

    # Add all the actions (subcommands)
    subparsers = parser.add_subparsers(
        title="actions",
        description="the program needs to know what action you want it to do.",
        help="those are all the possible actions")

    # Test command ###########################################################
    parser_test = subparsers.add_parser(
        "test",
        help="Run server tests.")
    parser_test.add_argument(
        "--fulltrace",
        default=False,
        action='store_true',
        help="Show the complete test log")
    parser_test.set_defaults(func=test)

    # Clean command ###########################################################
    parser_clean = subparsers.add_parser(
        "clean",
        help="Remove usuless and temp files from the folder.")
    parser_clean.set_defaults(func=clean)

    # Serve command ###########################################################
    parser_start = subparsers.add_parser(
        "start",
        help="Launch a tiny Ludobox web server.")
    parser_start.set_defaults(func=serve)

    parser_start.add_argument(
        "--debug",
        default=False,
        action='store_true',
        help="activate the debug mode of the Flask server (for development "
             "only NEVER use it in production).")
    parser_start.add_argument(
        "--port",
        default=None,
        help="define port to serve the web application.")

    # Returns the, now configured, parser
    return parser.parse_args(args)


def main(commands=None):
    """
    Launch command parser from real command line or from args.
    """
    # Configure the parser
    # commands.split()
    args = parse_args(sys.argv[1:])

    return args.func(**vars(args))  # We use `vars` to convert args to a dict

if __name__ == "__main__":
    main()
