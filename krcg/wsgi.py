"""Entrypoint for the WSGI app (web API)
"""
from . import flask

application = flask.create_app()
