import json

class Item:
    # def __init__(self, name, origin, icon="x"):
    #     self.name = name
    #     self.url = icon
    #     self.origin = origin
    #     self.games = {}

    def __init__(self, document):
        config = json.load(document)
        self.name = config.item_name
        self.url = config.icon_url
        self.origin = config.origin_game
        self.games = config.game_data
        return 

    def dump(self):
        config = {}
        config.item_name = self.name
        config.icon_url = self.url
        config.origin_game = self.origin
        config.game_data = self.games
        return json.dump(config)

    def check_game_version(self, game, verison):
        pass

    def generate_NFT(self, **kwargs):
        pass

    def get_hash():
        """ generate hash and result"""
        pass