from game_map import Game_Map
from unit import Unit
from orders import *

# set up map (Tunisia and surrounding seas)
map_source = {
    "ION": ["TYR", "TUN"],
    "TYR": ["ION", "TUN"],
    "TUN": ["TYR", "ION"]
}
game_map = Game_Map(map_source)

# units
f_ION = Unit("F", game_map.get_territory_by_name("ION"))
f_TYR = Unit("F", game_map.get_territory_by_name("TYR"))
f_TUN = Unit("F", game_map.get_territory_by_name("TUN"))

# assign orders
orders = [
    Move_Order(game_map, f_ION, game_map.get_territory_by_name("TUN")),
    Move_Order(game_map, f_TYR, game_map.get_territory_by_name("ION")),
    Move_Order(game_map, f_TUN, game_map.get_territory_by_name("TYR")),
]
root = orders[0]

# resolve
root.resolve(0)

print("\n\nSummary")
for order in orders:
    print(f"{order}: {order.succeeded}")