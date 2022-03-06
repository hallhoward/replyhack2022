import click
from flask import Flask, render_template
import json
import sqlite3
import requests
from random import randint
from time import sleep
from time import time
app = Flask(__name__)



# In orderto add item from minecraft to database use:
# 127.0.0.1:5000/new/<user>/<item_name>/<origin_game>

# In order to list items held by a user user:
# 127.0.0.1:5000/list/<user_id>


# Use a service account
prefix = "https://metaexchange-c9a99-default-rtdb.europe-west1.firebasedatabase.app"

# generate a random id of max length _limit_
def id(limit=10):
    return randint(1,10**limit)

# request a table 
def request(table):
    response = requests.get(f"{prefix}/{table}.json")
    return response.json()

# Provides the full JSON of a specific item
@app.route("/describe/<item_id>")
def describe_item():
    response = requests.get(f"{prefix}/items/{item_id}.json")
    return response.json()

# List all items
@app.route("/list")
def list_items():
    response = requests.get(f"{prefix}/items.json")
    return response.json()

# This is the method to list items in the wallet of a specific user
@app.route('/list/<user_id>')
def list_owned_items(user_id):
    response = requests.get(f"{prefix}/items.json")
    owned = []
    items = response.json()
    for item_id in items.keys():
        if items[str(item_id)]["owner"] == int(user_id):
            owned.append(item_id)
    return json.dumps(owned)

# Change ownership of an item. Sets user_id to own item_id
def chown(user_id, item_id):
    item_resp = requests.get(f"{prefix}/items/{item_id}.json")
    item_dict = item_resp.json()
    item_dict['owner'] = user_id
    return requests.patch(f"{prefix}/items/{item_id}.json", json=item_dict)

# Accept bid and perform trade
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

# Reject a bid
@app.route('/bid/reject/<bid_id>')
def reject_bid(bid_id):
    bid_r = requests.delete(f"{prefix}/bids/{bid_id}.json")
    return str(bid_id)

# Place a bid (user from holds offer items, user to holds the purchase items)
# after transaction, user_from will now obtain purchase and user_to will recieve offer
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
# set origin game to "minecraft" user to a single digit id 
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


@app.route("/web/list")
def web_list():
    item_list = list_items()
    html = ""
    for key in item_list.keys():
        item = item_list[str(key)]
        html += f"<h1>{item['item_name']}</h1>"
        html += f"<p>{json.dumps(item)}</p><br><br>"
    return html


@app.route("/web/trade/<trade_id>")
def trade_view(trade_id):
    trade_resp = requests.get(f"{prefix}/bids/{trade_id}.json")
    trade_json = trade_resp.json()
    item_ids = [*trade_json['purchase_items'], *trade_json['offer_items']]
    items = {}
    for i in item_ids:
        rsp = requests.get(f"{prefix}/items/{i}.json")
        items[str(i)] = rsp.json()
    html = ""
    html += f"<h1>User {trade_json['user_from']} has placed a bid to {trade_json['user_to']}.</h1>"
    html += "<br><br><br><br><br><br>"

    html += f"<h3>User {trade_json['user_from']} would like to purchase:</h3>"
    html += f"<ul>"
    for itemid in trade_json['purchase_items']:
        html += f"<li>{items[itemid]['item_name']}</li>"
    html += "</ul><br><br><br><br><br><br>"

    html += f"<h3>User {trade_json['user_to']} (You) would recieve in exchange:</h3>"
    html += f"<ul>"
    for itemid in trade_json['offer_items']:
        html += f"<li>{items[itemid]['item_name']}</li>"
    html += "</ul><br><br><br><br><br><br>"

    html+=f"<a href='/bid/accept/{trade_id}'>Accept bid</a><br>"
    html+=f"<a href='/bid/reject/{trade_id}'>Reject bid</a>"

    return html