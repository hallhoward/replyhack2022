class User:
    def __init__(self, document):
        config = json.load(document)
        self.username = config.keys()[0]
        self.items = config[self.username].items

    def dump(self):
        config = {
            f"{self.username}": {
                "password": f"{self.password}",
                "items": self.items
            }
        }
        return json.dump(config)