import argparse
import sys

import frontend
import problems


class Args(argparse.Namespace):
    input_file: str
    output_file: str


def parse_arguments() -> Args:
    parser = argparse.ArgumentParser(description='compiler for COL objects')

    parser.add_argument(
        '-i', '--input',
        type=str,
        help='input file',
        dest='input_file',
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='output file',
        dest='output_file',
    )

    return parser.parse_args(namespace=Args())


def main(args: Args, text: str):
    frontend.parse(text)


if __name__ == '__main__':
    args = parse_arguments()

    # TODO: add error handling for reading
    with open(args.input_file, 'r') as f:
        text = f.read()

    try:
        main(args, text)
    except problems.InternalProblem as e:
        print(e.render(), file=sys.stderr)
    except problems.FatalProblem as e:
        print(e.render(text), file=sys.stderr)
