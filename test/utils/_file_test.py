from pathlib import Path


def _do_file_test(self, file: Path):
    with file.open() as f:
        lines = f.readlines()

    inputs = {}
    current = None

    # add every line to the right input field
    for line in lines:
        line = line.rstrip('\n')

        if line.startswith('#'):
            name = line[1:].strip().lower().replace(' ', '_')

            current = inputs.get(name, [])
            inputs[name] = current
        else:
            current.append(line)

    # remove trailing empty lines
    for value in inputs.values():
        while len(value) > 0 and value[-1] == '':
            value.pop()

    self.do_test(**{name: '\n'.join(value) for name, value in inputs.items()})


class FileTestMeta(type):
    def __new__(mcs, name, bases, dct, **kwargs):
        def create_file_test(f):
            return lambda self: _do_file_test(self, f)

        for file in Path(kwargs['path']).parent.iterdir():
            if not file.is_file() or file.suffix != '.test':
                continue

            dct[f'test_{file.stem}'] = create_file_test(file)

        return type.__new__(mcs, name, bases, dct)
