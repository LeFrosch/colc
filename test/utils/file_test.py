from pathlib import Path


def _do_file_test(self, file: Path):
    with file.open() as f:
        lines = f.readlines()

    input_lines = []
    output_lines = []

    current = None

    for line in lines:
        line = line.rstrip('\n')

        if line == '# INPUT':
            current = input_lines
        elif line == '# OUTPUT':
            current = output_lines
        elif current is not None:
            current.append(line)

    self.assertTrue(len(input_lines) > 0, 'no input found')
    self.assertTrue(len(output_lines) > 0, 'no output found')

    self.do_test('\n'.join(input_lines), '\n'.join(output_lines))


class FileTestMeta(type):
    def __new__(mcs, name, bases, dct, **kwargs):
        def create_file_test(f):
            return lambda self: _do_file_test(self, f)

        for file in Path(kwargs['path']).parent.iterdir():
            if not file.is_file() or file.suffix != '.test':
                continue

            dct[f'test_{file.stem}'] = create_file_test(file)

        return type.__new__(mcs, name, bases, dct)
