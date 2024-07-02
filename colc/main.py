import argparse
import sys

from colc.frontend import parse
from colc.problems import InternalProblem, FatalProblem

from .__about__ import __version__, __description__


class Args(argparse.Namespace):
    input_file: str
    output_file: str


def parse_arguments() -> Args:
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument(
        '--version',
        type=bool,
        help='print version and exit',
    )

    parser.add_argument(
        '-i',
        type=str,
        help='path to the input file',
        dest='input_file',
    )

    parser.add_argument(
        '-o',
        type=str,
        help='path to the output file',
        dest='output_file',
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
        parse(text)
    except InternalProblem as e:
        print(e.render(), file=sys.stderr)
    except FatalProblem as e:
        print(e.render(text), file=sys.stderr)
