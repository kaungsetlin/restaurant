from app import create_app
from flask import g

app = create_app()

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
