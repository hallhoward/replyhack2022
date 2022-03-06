import click
from flask import Flask
import json
import sqlite3
import requests
from random import randint
from time import sleep
from time import time
app = Flask(__name__)
# Use a service account
prefix = "https://metaexchange-c9a99-default-rtdb.europe-west1.firebasedatabase.app"
def id(limit=10):
    return randint(1,10**limit)


def request(table):
    response = requests.get(f"{prefix}/{table}.json")
    return response.json()

@app.route("/describe/<item_id>")
def describe_item():
    response = requests.get(f"{prefix}/items/{item_id}.json")
    return response.json()


@app.route("/list")
def list_items():
    response = requests.get(f"{prefix}/items.json")
    return response.json()

# This is the method to list items in the wallet
@app.route('/list/<user_id>')
def list_owned_items(user_id):
    response = requests.get(f"{prefix}/items.json")
    owned = []
    items = response.json()
    for item_id in items.keys():
        if items[str(item_id)]["owner"] == int(user_id):
            owned.append(item_id)
    return json.dumps(owned)

def chown(user_id, item_id):
    item_resp = requests.get(f"{prefix}/items/{item_id}.json")
    item_dict = item_resp.json()
    item_dict['owner'] = user_id
    return requests.patch(f"{prefix}/items/{item_id}.json", json=item_dict)


@app.route('/bid/accept/<bid_id>')
def accept_bid(bid_id):
    bid_r = requests.get(f"{prefix}/bids/{bid_id}.json")
    bid_d = bid_r.json()
    bid_d['time'] = int(time())
    hist_d = {str(bid_id):bid_d}
    u_from = bid_d['user_from']
    u_to = bid_d['user_to']
    for i_purchase in bid_d['purchase_items']:
        chown(u_from, i_purchase)
    for i_offer in bid_d['offer_items']:
        chown(u_to, i_offer)
    requests.put(f"{prefix}/prev.json", json=hist_d)
    requests.delete(f"{prefix}/bids/{bid_id}.json")
    return {"success": "true"}


@app.route('/bid/reject/<bid_id>')
def reject_bid(bid_id):
    bid_r = requests.delete(f"{prefix}/bids/{bid_id}.json")
    return str(bid_id)


@app.route("/bid/<user_from>/<user_to>/<purchase>/<offer>")
def place_bid(user_from, user_to, purchase, offer):
    bid_id = id()
    bid_dict = {
        f"{bid_id}": {
            "user_from": user_from,
            "user_to": user_to,
            "purchase_items": [purchase],
            "offer_items": [offer]
        }
    }
    requests.patch(f"{prefix}/bids.json", data=json.dumps(bid_dict))
    return f"Created new bid with id {bid_id}"


# This is the method to call from minecraft to add the item to the wallet
@app.route("/new/<user>/<item_name>/<origin_game>")
def construct_item(user, item_name, origin_game):
    item_id = id(2)
    item_json = {
        str(item_id): {
            "item_name": item_name,
            "icon_url": "#",
            "origin_game": origin_game,
            "game_data":{
                "minecraft":{
                    "min_version": "1.0.0",
                    "server": "*"
                }
            },
            "owner": user
        }
    }
    response = requests.patch(f"{prefix}/items.json", data=json.dumps(item_json))
    return str(item_id)



# If in double, purchase from and offer to. That the end state