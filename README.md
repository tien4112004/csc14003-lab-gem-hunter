# Gem Hunter Solver

A SAT-solver and traditional solvers (brute force and backtracking) for the Gem Hunter puzzle game.

## Problem Description

In the Gem Hunter game, you are given a grid with some cells containing numbers from 1-8, and others empty (marked with "\_"). The goal is to determine which cells contain traps ("T") and which contain gems ("G") according to the following rules:

1. The number in a cell indicates exactly how many trap cells are surrounding it (in the 8 adjacent cells).
2. An unreachable cell (surrounded by all empty cells) must remain empty.
3. A cell is a gem when all surrounding cells are number cells, gem cells, or empty (i.e., no surrounding traps).

## Environment

- Ubuntu 25.04
- Python 3.9 or higher.

## Installation

First, clone the repository

```bash
git clone https://github.com/yourusername/gem-hunter.git
cd gem-hunter
```

Then create a virtual environment and install the dependencies

```bash
make install
```

- This will create a virtual environment in the `venv` directory and install all required packages listed in `requirements.txt`.

- If error occured, you can manually create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Solvers Implemented

1. **SAT Solver**: Uses the pysat library to convert the puzzle into CNF form and solve it.
2. **Brute Force**: Tries all possible combinations of trap and gem placements.
3. **Backtracking**: Uses backtracking with constraint propagation for faster solving.

## Usage

### Main Program

- To run the main program, use the following command:

```bash
make run
```

- If error occurred, you can run the main program directly:

```bash
python3 main.py
```

This provides a simple UI for selecting different functions:

- Generate new maps
- Solve maps with different solvers
- Run benchmarks
- View CNF explanations

### Solver Command Line Interface

```bash
python solver_cli.py
```

Provides a more detailed CLI with the following options:

- Generate maps
- Solve maps using different solvers
- Run benchmarks
- View CNF explanations

### Map Generator

```bash
python map_generator.py
```

An interactive generator will be launched. You can choose the number of maps, max_size and min_size of the maps, and the trap probability. By default, the generator will create a folder called `maps` with the generated maps.
