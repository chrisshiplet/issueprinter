# issueprinter
Small set of python utilities for running a GitHub Issue Printer on a Raspberry Pi + Adafruit Thermal Printer

## Setup

For Development:
* `git submodule update --init --recursive`
* `sqlite3 printer.db < install.sql`
* `pip install Flask`

On the Pi:
* `sudo apt-get install python-serial python-imaging python-unidecode sqlite3`
* `git submodule update --init --recursive`
* `sqlite3 printer.db < install.sql`
* `pip install Flask`

Webhook:
* Create a new GitHub webhook pointing to `http://hostname:4000/` with content type `application/json` and a secret, if desired
* Select only the "Issues" event

## Running

### Environment Variables

* `APP_ENV` can be set to `production` to turn off stack traces and debug messages, otherwise defaults to `development` with full stack traces enabled
* `APP_SECRET` can be set, requiring a matching secret on the webhook to prevent randos from sending print tasks

### Starting the App

* `python server.py` starts the app listening on port 4000
