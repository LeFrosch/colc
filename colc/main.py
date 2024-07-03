import argparse
import sys
import pickle

from colc.frontend import parse
from colc.backend import process
from colc.common import InternalProblem, FatalProblem

from .__about__ import __version__, __description__


class Args(argparse.Namespace):
    input_file: str
    output_file: str


def parse_arguments() -> Args:
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument(
        '--version',
        action='store_true',
        help='print version and exit',
    )

    parser.add_argument(
        '-i',
        type=str,
        help='path to the input file',
        dest='input_file',
        required=True,
    )

    parser.add_argument(
        '-o',
        type=str,
        help='path to the output file',
        dest='output_file',
        required=True,
    )

    return parser.parse_args(namespace=Args())


def main():
    args = parse_arguments()

    if args.version:
        print(__version__)
        return

    # TODO: add error handling for reading
    with open(args.input_file, 'r') as f:
        text = f.read()

    try:
        obj = process(parse(text))
    except InternalProblem as e:
        print(e.render(), file=sys.stderr)
        return
    except FatalProblem as e:
        print(e.render(text), file=sys.stderr)
        return

    # TODO: add error handling for writing
    with open(args.output_file, 'wb') as f:
        pickle.dump(obj, f)
