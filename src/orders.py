UNRESOLVED = 0
GUESSING = 1
RESOLVED = 2


class Order:
    def __init__(self, game_map, unit):
        self.game_map = game_map
        self.unit = unit
        self.location = self.unit.location
        self.nationality = self.unit.nationality
        self.dependencies = []

        self.state = UNRESOLVED
        self.succeeded = False # means nothing currently since self.state = UNRESOLVED

    def get_dependencies(self, orders):
        return orders

    def get_adjacent_orders(self):
        adjacent_orders = list(filter(lambda order: order != None, [self.game_map.get_order_at(location) for location in self.game_map.get_neighbors(self.location)]))
        return adjacent_orders

    def resolve(self):
        # resolve recursively
        self.state = GUESSING
        for dep in self.dependencies:
            if dep.state != GUESSING: # nothing circular has happened
                dep.resolve()
            else:
                # TODO: handle circular occurences (fleet paradox, triple swaps, etc.)
                if isinstance(self, Hold_Order) and isinstance(dep, Move_Order):
                    self.location.resolve_conflict()
                elif isinstance(self, Move_Order) and isinstance(dep, Hold_Order):
                    dep.location.resolve_conflict()

    
    def handle_success(self):
        pass

    def handle_failure(self):
        pass


class Hold_Order(Order):
    def __init__(self, game_map, unit):
        Order.__init__(self, game_map, unit)
        self.location.add_claim(self)
        self.strength = 1

    def get_dependencies(self, orders):
        # returns the move orders and support hold orders directed at this location\
        # TODO: make this function look more like Move_Order.get_dependencies
        move_orders = list(filter(lambda order: isinstance(order, Move_Order)))
        support_orders = list(filter(lambda order: isinstance(order, Support_Hold_Order)))
        dependent_orders = list(filter(lambda order: order.target == self.location) for order in move_orders + support_orders)
        return dependent_orders


class Move_Order(Order):
    def __init__(self, game_map, unit, target):
        Order.__init__(self, game_map, unit)
        self.target = target
        self.target.add_claim(self)
        self.convoy_failed = False
        self.strength = 1

    def get_dependencies(self, orders):
        # returns the move orders whose targets match self.target
        # and any orders whose locations match self.target
        def is_relevant(order):
            if isinstance(order, Move_Order):
                if order.target == self.target:
                    return True
            elif isinstance(order, Support_Move_Order):
                if order.move_target == self.target and order.move_origin == self.location:
                    return True
            elif order.location == self.target:
                return True
            return False
        dependencies = [order for order in orders if is_relevant(order)]
        return dependencies

    def resolve(self):
        # resolve this order, checking dependencies

        # determine dependencies
        adjacent_orders = self.get_adjacent_orders()
        self.dependencies = self.get_dependencies(adjacent_orders)

        # resolve recursively
        super().resolve()

        # this is a move order


class Support_Order(Order): # should not be directly instanced
    def __init__(self, game_map, unit):
        Order.__init__(self, game_map, unit)

    def get_dependencies(self, orders):
        # return move orders whose targets match self.location
        def is_relevant(order):
            if isinstance(order, Move_Order):
                if (order.target == self.location):
                    return True
            return False
        dependencies = [order for order in orders is is_relevant(order)]
        return dependencies

    def resolve(self):
        # resolve this order, checking dependencies

        # determine dependencies
        adjacent_orders = self.get_adjacent_orders()
        self.dependencies = self.get_dependencies(adjacent_orders)

        # resolve recursively
        super().resolve()

        # this is a support order, so it will fail if any deps succeed
        if any([dep.succeeded for dep in self.dependencies]):
            self.succeeded = False
        else: # Note: this will result in success if there are no deps
            self.succeeded = True

        if self.succeeded:
            self.handle_success()
        else:
            self.handle_failure()
        self.state = RESOLVED


class Support_Hold_Order(Support_Order):
    def __init__(self, game_map, unit, target):
        Support_Order.__init__(self, game_map, unit)
        self.target = target
        self.hold_order = self.game_map.get_order_at(self.target)
        if not isinstance(self.hold_order, Hold_Order):
            self.state = RESOLVED
            self.succeeded = False

    def handle_success(self):
        self.hold_order.strength += 1


class Support_Move_Order(Support_Order):
    def __init__(self, game_map, unit, move_target, move_origin):
        Support_Order.__init__(self, game_map, unit)
        self.move_target = move_target
        self.move_origin = move_origin
        self.move_order = self.game_map.get_order_at(self.move_origin)
        if not isinstance(self.move_order, Move_Order):
            self.state = RESOLVED
            self.succeeded = False
            

    def handle_success(self):
        self.move_order.strength += 1


class Convoy_Order(Order):
    def __init__(self, game_map, unit, army_target, army_origin):
        Order.__init__(self, game_map, unit)
        self.army_target = army_target
        self.army_origin = army_origin
