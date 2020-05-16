# -*- coding: utf-8 -*-
"""
A validation script
"""

import argparse
import sys
import logging
from pathlib import Path

from property_rosetta import __version__
from property_rosetta.dictionary import Dictionary, DictionaryError

__author__ = "Claudio Bantaloukas"
__copyright__ = "Claudio Bantaloukas"
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Validate a dictionary")
    parser.add_argument(
        "--version",
        action="version",
        version="property_rosetta {ver}".format(ver=__version__))
    parser.add_argument(
        dest="path",
        help="path containing a dictionary",
        type=Path)
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO)
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug(f"Loading dictionary from {args.path}")
    try:
        dictionary = Dictionary.from_yaml_dictionary(args.path)
    except DictionaryError as e:
        _logger.fatal(f"{e}")
        return 1
    errors = dictionary.validate()
    if not errors:
        _logger.info('No errors found')
        return 0
    else:
        for error in errors:
            _logger.error(error)
        return 1


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
