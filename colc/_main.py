import argparse
import sys

from colc.backend import Config
from colc.common import InternalProblem, FatalProblem, write_file

from ._compile import compile
from ._encode import encode, Compression
from ._debug import print_debug_info
from .__about__ import __version__, __description__


class Args(argparse.Namespace):
    input_file: str
    output_file: str
    compression: Compression
    optimization: list[str]


def parse_arguments() -> Args:
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument(
        '--version',
        action='version',
        version=__version__,
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='path to the input file',
    )

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='path to the output file',
        dest='output_file',
        default='out.colo',
    )

    parser.add_argument(
        '-c',
        '--compress',
        type=Compression,
        help='compression to apply to the object',
        dest='compression',
        default=Compression.NONE,
    )

    parser.add_argument(
        '-O',
        '--optimization',
        type=str,
        nargs='+',
        help='enable or disable specific optimizations',
        dest='optimization',
    )

    parser.add_argument(
        '--dbg',
        action='store_true',
        default=False,
        help='prints debug information of the object',
        dest='debug',
    )

    return parser.parse_args(namespace=Args())


def main():
    args = parse_arguments()

    try:
        obj = compile(args.input_file, Config(optimizations=args.optimization))

        if args.debug:
            print_debug_info(obj)

        raw = encode(obj, compression=args.compression)
        write_file(args.output_file, raw)
    except (InternalProblem, FatalProblem) as e:
        print(e.render(), file=sys.stderr)
    except AssertionError as e:
        print(InternalProblem('assertion failed', e).render(), file=sys.stderr)
