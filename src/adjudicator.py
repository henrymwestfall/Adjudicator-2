from game_map import Game_Map
from unit import Unit
from orders import *

# set up map (currently just France for testing)
map_source = {
    "BRE": ["PIC", "PAR", "GAS", "ENG"],
    "PAR": ["PIC", "BUR", "GAS", "BRE"],
    "GAS": ["BRE", "PAR", "MAR"],
    "PIC": ["BUR", "PAR", "BRE", "ENG"],
    "BUR": ["PIC", "PAR", "MAR", "GAS"],
    "MAR": ["BUR", "GAS"],
    "ENG": ["BRE", "PIC"]
}
game_map = Game_Map(map_source)


# units
a_BRE = Unit("A", game_map.get_territory_by_name("BRE")) # pretend it's French
a_PAR = Unit("A", game_map.get_territory_by_name("PAR")) # pretend it's French
a_GAS = Unit("A", game_map.get_territory_by_name("GAS")) # pretend it's French

a_MAR = Unit("A", game_map.get_territory_by_name("MAR")) # pretend it's Italian

a_BUR = Unit("A", game_map.get_territory_by_name("BUR")) # pretend it's German
a_PIC = Unit("A", game_map.get_territory_by_name("PIC")) # pretend it's German

f_ENG = Unit("F", game_map.get_territory_by_name("ENG")) # pretend it's English

# assign orders. Note this is a backwards way of doing this
# and may be changed later
orders = [
    Hold_Order(game_map, a_PAR), # A Par H
    Support_Hold_Order(game_map, a_BRE, game_map.get_territory_by_name("PAR")), # A Bre S A Par H
    Move_Order(game_map, a_GAS, game_map.get_territory_by_name("MAR")), # A Gas -> Mar

    Move_Order(game_map, a_BUR, game_map.get_territory_by_name("PAR")), # A Bur -> Par
    Support_Move_Order(game_map, a_PIC, game_map.get_territory_by_name("PAR"), game_map.get_territory_by_name("BUR")), # A Pic S A Bur -> Par

    Support_Move_Order(game_map, a_MAR, game_map.get_territory_by_name("PAR"), game_map.get_territory_by_name("BUR")), # A Mar S A Bur -> Par

    Move_Order(game_map, f_ENG, game_map.get_territory_by_name("BRE")) # F Eng -> Bre
]
root = orders[0]


# resolve everything
root.resolve(0)

print("\n\nSummary")
for order in orders:
    print(f"{order}: {order.succeeded}")