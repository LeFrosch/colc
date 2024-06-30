INPUT='/dev/stdin'
OUTPUT='/dev/stdout'

.venv/bin/activate: requirements.txt
	python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt

run: .venv/bin/activate
	.venv/bin/python3 main/main.py --input $(INPUT) --output $(OUTPUT)

test: .venv/bin/activate
	PYTHONPATH=main .venv/bin/python3 -m unittest discover -s test -v

clean:
	find . -name .venv -prune -o -name __pycache__ | xargs rm -rf

.PHONY: run clean test
