from random import randint
import requests
import json
# for uf in range(1,11):
#     for ut in range(1,11):
#         pl = randint(1,1000)
#         ol = randint(1,1000)
#         requests.get(f"http://127.0.0.1:5000/bid/{uf}/{ut}/{pl}/{ol}")
        
# json = """
# {
#     "<item_id>":{
#         "item_name": "Wooden Sword",
#         "icon_url": "https://static.wikia.nocookie.net/minecraft_gamepedia/images/d/d5/Wooden_Sword_JE2_BE2.png/revision/latest/scale-to-width-down/160?cb=20200217235747",
#         "origin_game": "minecraft",
#         "game_data":{
#             "minecraft":{
#                 "min_version": "1.0.0",
#                 "server": "*"
#             }
#         },
#         "owner":100
#     }
# }"""
prefix = "https://metaexchange-c9a99-default-rtdb.europe-west1.firebasedatabase.app"

for i in range(1000):
    requests.delete(f"{prefix}/items/{i}.json")