import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    results = cur.fetchall()
    cur.close()
    return (results[0] if results else None) if one else results

def to_object(x):
    if not x or x is None:
        return None
    elif not isinstance(x, list):
        obj = {}
        for col in x.keys():
            obj[col] = x[col]
        return obj
    else:
        cols = x[0].keys()
        obj_list = []
        for item in x:
            obj = {}
            for col in cols:
                obj[col] = item[col]
            obj_list.append(obj)
        return obj_list
