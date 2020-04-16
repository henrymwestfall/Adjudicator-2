# Diplomacy Adjudicator

An adjudicator for the Diplomacy board game written in Python.

Currently does not handle circular dependencies correctly in most cases. Furthermore, orders and units must be hardcoded into
`adjudicator.py` since there is no parsing function.

To display the outcome of the orders, run `python3 adjudicator.py`. The only dependency (currently) is a version of Python 3.

## Creating a Map

Maps are created from source dictionaries. The source dictionary must map territory names to a list of neighboring territories.
The game map does not infer bidirectionality.

Example:
```python
from game_map import Game_Map

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
```

## Creating New Units

Currently, new units must be coded into `adjudicator.py`. Units must be instances of `unit.Unit`.
The Unit constructor takes 2 arguments: `unit_type` and `territory`. `unit_type` must be `"A"` or `"F"`, representing an Army
or a Fleet respectively. `territory` must be a `Territory` object. Use `game_map.Game_Map.get_territory_by_name` to get a territory object
by it's name. Nationality is not yet implemented.

Example:
```python
from unit import Unit

f_BRE = Unit("F", game_map.get_territory_by_name("BRE")) # pretend this is French
f_PIC = Unit("F", game_map.get_territory_by_name("PIC")) # pretend this is French
a_PAR = Unit("A", game_map.get_territory_by_name("PAR")) # pretend this is German
a_GAS = Unit("A", game_map.get_territory_by_name("GAS")) # pretend this is German
```

## Assigning Orders

To assign an order, instantiate an order of the correct type and pass the applicable parameters to the constructor. Currently,
convoy orders are not implemented and thus should not be used. Orders do not have to be stored anywhere, but it is recommended
that they are stored in an iterable for easier reference later.

To resolve an order, call `Order.resolve(0)`. The argument is the number of debug tabs you want in the outer layer.

Example:
```python
from orders import Hold_Order, Move_Order, Support_Hold_Order, Support_Move_Order

order_set = [
  Hold_Order(game_map, f_BRE),
  Support_Hold_Order(game_map, f_PIC, game_map.get_territory_by_name("BRE")),
  
  Move_Order(game_map, a_PAR),
  Support_Move_Order(game_map, a_GAS, game_map.get_territory_by_name("BRE"), game_map.get_territory_by_name("PAR"))
]
root = order_set[0]
root.resolve(0)
```
