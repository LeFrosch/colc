# COL object compiler
This is a compiler for the Collaborative Optimization Language or short COL.

## Usage
To install the compiler into your local virtual environment, run the following command:
```shell
make install
```
After successful installation, the `colc` compiler command should be available within your virtual environment. You can 
confirm your installation by checking the version of the installed compiler using:
```shell
colc --version
```
To retrieve more information about the command-line interface and its usage, refer to the built-in help command.

To compile a COL file run the following command:
```shell
colc file.col
```
This command should produce an `out.colo` object file.

## Development
To run the project's test suite, use the test make target. Run the following command:
```shell
make test
```
Also, further CI checks can be executed with the check make target. Run the following command:
```shell
make check
```
These checks utilize [ruffs](https://github.com/astral-sh/ruff) linter and formatter.