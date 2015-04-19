#!/usr/bin/python
import os
import sqlite3
import hashlib
import hmac
import json
from datetime import *
from flask import Flask, abort, jsonify, request, g
from werkzeug import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('printer.db')
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app = Flask(__name__)
app_env = os.getenv('APP_ENV', 'development')
app_secret = os.getenv('APP_SECRET', '')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    if code == 500:
        app.logger.error(e)
    return jsonify(error=str(e)), code

# manually assign error handler for every possible status code...
for code in HTTP_STATUS_CODES:
    app.register_error_handler(code, handle_error)

@app.route('/ping/', methods=['GET',])
def ping():
    return('', 200)

@app.route('/', methods=['GET',])
def queue_get():
    rows = query_db('select * from issue_queue order by id desc limit 100')
    rv = []
    for row in rows:
        rv.append({
            'id': row[0],
            'timestamp': row[1],
            'status': row[2],
            'url': row[3],
            'repo': row[4],
            'number': row[5],
            'title': row[6],
            'assignee': row[7],
            'labels': row[8]
        })
    return json.dumps(rv)

@app.route('/', methods=['POST',])
def queue_post():
    payload = request.get_json()
    date = request.headers.get("Date", "")

    # abort on non-JSON payload
    if payload is None:
        app.logger.warning('Non-JSON request received, aborting')
        return ('', 400)

    # APP_SECRET environment variable is set, try to validate against GitHub's webhook secret
    if app_secret != '':
        message_hmac = hmac.HMAC(app_secret, request.get_data() + date, hashlib.sha1)
        local_signature = message_hmac.hexdigest()
        remote_signature = request.headers.get('X-Hub-Signature', '')

        # abort if APP_SECRET is set but no signature was provided in the request
        if remote_signature is '':
            app.logger.warning('APP_SECRET set but no X-Hub-Signature provided, aborting')
            return ('', 403)
        else:
            # extract the sha1 signature from 'sha1=asdfghjkl' format
            try:
                remote_signature = remote_signature.split('=')[1]
            # abort on invalid sha1 hash
            except IndexError:
                app.logger.warning('Invalid X-Hub-Signature provided, aborting')
                return ('', 403)

        # abort if signatures don't match
        if local_signature != remote_signature:
            app.logger.warning('X-Hub-Signature did not match APP_SECRET, aborting')
            return ('', 403)

    # abort if action type missing
    if 'action' not in payload:
        app.logger.warning('Action type missing, aborting')
        return ('', 400)

    # abort on non-assignment notifications
    if payload['action'] not in ['unassigned', 'assigned']:
        app.logger.debug('Invalid action ' + payload['action'] + ', ignoring')
        return ('', 400)

    # remove existing issue assignments each time to prevent dupes
    query_db('delete from issue_queue where url = ? and status = ?', (payload['repository']['url'], 'new'))

    # convert timestamp to az time for logging
    timestamp = payload['issue']['updated_at']
    timestamp_dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=7)
    timestamp_dt_str = timestamp_dt.strftime('%b %d %Y %H:%M:%S')

    # abort now if this was an unassignment
    if payload['action'] == 'unassigned':
        app.logger.debug('%s #%s "%s" unassigned at %s' % (payload['repository']['name'], str(payload['issue']['number']), payload['issue']['title'], timestamp_dt_str))
        return ('', 202)
    # otherwise proceed to add assignment to print queue
    else:
        # convert labels to comma separated list
        labels = []
        for label in payload['issue']['labels']:
            labels.append(label['name'])
        labels = ','.join(map(str, labels))

        # execute query
        query_db('insert into issue_queue (timestamp, status, url, repo, number, title, assignee, labels) values (?, ?, ?, ?, ?, ?, ?, ?)', (timestamp, 'new', payload['repository']['url'], payload['repository']['name'], payload['issue']['number'], payload['issue']['title'], payload['assignee']['login'], labels))

        # log assignment and return 202 accepted
        app.logger.debug('%s #%s "%s" %s to %s at %s with labels [%s]' % (payload['repository']['name'], str(payload['issue']['number']), payload['issue']['title'], payload['action'], payload['assignee']['login'], timestamp_dt_str, labels))
        return ('', 202)

# bootstrap flask app
if __name__ == '__main__':
    if app_env == 'production':
        app.run(host='0.0.0.0',port=4000,debug=False)
    else:
        app.run(host='0.0.0.0',port=4000,debug=True)
