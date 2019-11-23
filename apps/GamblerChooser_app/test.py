players = [{"name": "john"}]
players[0]["hand"] = [1,2,3,4,5]
players[0]["best_hand"] = {
                "type": "None",
                "value": 0,
                "high_card": 0,
                "suit": 0
            }
players[0]["best_hand"]["value"] = 2
print(players)