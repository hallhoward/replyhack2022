import click
from flask import Flask
import json
import sqlite3

app = Flask(__name__)

@app.route("/")
def hi():
    return {1:{2:3}}