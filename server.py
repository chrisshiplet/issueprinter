from flask import Flask, request, g
import os
import sqlite3
import json

app = Flask(__name__)

app_env = os.getenv('APP_ENV', 'development')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('printer.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def root():
    return 'issue printer 0.0.1'

@app.route('/queue/', methods=['GET', 'POST'])
def queue_endpoint():
    if request.method == 'GET':
        rows = query_db('select * from issue_queue where status != \'complete\'')
        return json.dumps(rows)
    else:
        return 'POST /queue/ not implemented yet'

if __name__ == '__main__':
    if app_env == 'production':
        app.run(host='0.0.0.0')
    else:
        app.run(debug=True)
