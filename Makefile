.PHONY: run cnf generate install clean clean-testcase clean-cnf

VENV_DIR=venv
ACTIVATE_LINUX:=. venv/bin/activate
PYTHON3=./${VENV_DIR}/bin/python3
PIP=./${VENV_DIR}/bin/pip

all: run

run:
	@echo "Running Gem Hunter main program..."
	@$(PYTHON3) main.py

generate:
	@echo "Generating testcase..."
	@$(PYTHON3) main.py --generate --size 10 --probability 0.2

install:
	@echo "Setting up the environment..."
	@python3 -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	@$(PIP) install -r requirements.txt

clean:
	@echo "Cleaning up the environment..."
	@rm -rf __pycache__/
	@rm -f testcase/solution/*.txt

clean-testcase:
	@echo "Cleaning up testcase..."
	@rm -rf testcase

clean-cnf:
	@echo "Cleaning up CNF explanations..."
	@rm -rf *.cnf cnf/
