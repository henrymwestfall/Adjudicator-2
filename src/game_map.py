from territory import Territory


class Game_Map:
    def __init__(self, source_map):
        self.source_map = source_map
        self.game_map = {}

        self.territories_by_name = {}

        for territory_name, neighbors in self.source_map.items():
            if not territory_name in self.territories_by_name:
                territory = Territory(territory_name)
                self.territories_by_name[territory_name] = territory
            else:
                territory = self.territories_by_name[territory_name]
            
            self.game_map[territory] = []

            for n in neighbors:
                if not n in self.territories_by_name:
                    n_territory = Territory(n)
                    self.territories_by_name[n] = n_territory
                else:
                    n_territory = self.territories_by_name[n]
                
                self.game_map[territory].append(n_territory)
        
    def get_neighbors(self, territory):
        # get a list of the territory's neighbors
        return self.game_map[territory]

    def connected(self, territory_a, territory_b):
        # check if two territories are connected
        # this ignores the terrain of the territory
        return territory_b in self.game_map[territory_a]

    def get_order_at(self, territory):
        # get the order of the unit at passed territory (may return None)
        if territory.unit == None:
            return None
        else:
            return territory.unit.order

    def get_territory_by_name(self, name):
        return self.territories_by_name[name]

