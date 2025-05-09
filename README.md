# Gem Hunter

## Installation

First, clone the repository

```bash
git clone
```

Then create a virtual environment and install the dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Dump the requirements to a file

```bash
pip freeze > requirements.txt
```

## Usage

### Map generator

```bash
python map_generator.py
```

An interactive generator will be launched. You can choose the number of maps, max_size and min_size of the maps, and the number of gems. By defallt, the generator will create a folder called `maps` with the generated maps.
