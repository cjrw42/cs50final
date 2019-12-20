#!/usr/bin/env bash
export FLASK_ENV=development
export FLASK_APP=application.py
export FLASK_RUN_PORT=8000
flask run --host=0.0.0.0