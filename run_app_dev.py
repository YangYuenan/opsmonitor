#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import create_app
from app.models import db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.before_request
def _db_connect():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
