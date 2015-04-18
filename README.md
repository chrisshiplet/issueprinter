# issueprinter
Small set of python utilities for running a GitHub Issue Printer on a Raspberry Pi + Adafruit Thermal Printer

## Setup

For Development:
* `git submodule update --init --recursive`
* `sqlite3 printer.db < install.sql`
* `pip install Flask`

On the Pi:
* `sudo apt-get install python-serial python-imaging python-unidecode`
* `git submodule update --init --recursive`
* `sqlite3 printer.db < install.sql`
