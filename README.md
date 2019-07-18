# python_utils
This repository contains multiple python utils, such as:

simple tkinter GUI, configuration, file and dataframe manager, logger, date utils, and various other models or utils.

## Installation
1) Install python 3.5+ (prefer not to use Anaconda as some issues have already occured with pandas/numpy libraries)

For example, install WinPython distribution (Windows): https://winpython.github.io/

For Linux distributions, `sudo apt install python3` should work as well.

2) Preferably install a virtual environment in `tools/venv/`

* Open a terminal (cmd in Windows)

* Type `pip install virtualenv` or `python3 -m pip install virtualenv` (Linux) / `python -m pip install virtualenv` (Windows)

* Type `virtualenv tools/venv` (precise python 3 if needed)

3) Install requirements in the virtual environment:

`source tools/venv/Scripts/activate` (Windows) or `source tools/venv/bin/activate` (Linux)

`pip install - requirements.txt`

4) You're done!
