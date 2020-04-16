UNRESOLVED = 0
GUESSING = 1
RESOLVED = 2


class Order:
    def __init__(self, game_map, unit):
        self.game_map = game_map
        self.unit = unit
        self.unit.order = self
        self.territory = self.unit.territory
        self.nationality = self.unit.nationality
        self.dependencies = []

        self.state = UNRESOLVED
        self.succeeded = False # means nothing currently since self.state = UNRESOLVED

    def get_dependencies(self, orders):
        return orders

    def get_adjacent_orders(self):
        adjacent_orders = list(filter(lambda order: order != None, [self.game_map.get_order_at(territory) for territory in self.game_map.get_neighbors(self.territory)]))
        return adjacent_orders

    def resolve(self, debug_tabs):
        # resolve recursively
        self.state = GUESSING
        guessing_deps = []
        print("\t"*debug_tabs+"Resolving", self)
        for dep in self.dependencies:
            if dep.state == UNRESOLVED: # nothing circular has happened
                dep.resolve(debug_tabs + 1)
            else:
                print("\t"*(debug_tabs+1)+"Revisiting", dep)
                guessing_deps.append(dep)
        
        # handle guessing deps
        for dep in guessing_deps:
            if dep.state != GUESSING:
                print("\t"*debug_tabs+f"GUESSING dependency ({dep}) was resolved elsewhere")
                continue
            # TODO: handle circular occurences (fleet paradox, triple swaps, etc.)
            # ensure this dep has resolved all non-guessing deps
            if not any([depdep.state == UNRESOLVED for depdep in dep.dependencies]):
                if isinstance(self, Hold_Order) and isinstance(dep, Move_Order):
                    self.territory.resolve_conflict()
                elif isinstance(self, Move_Order) and isinstance(dep, Hold_Order):
                    dep.territory.resolve_conflict()
            else:
                dep.resolve(debug_tabs + 1)
        
        self.state = RESOLVED

    
    def handle_success(self):
        pass

    def handle_failure(self):
        pass


class Hold_Order(Order):
    def __init__(self, game_map, unit):
        Order.__init__(self, game_map, unit)
        self.territory.add_claim(self)
        self.strength = 1

    def __str__(self):
        return f"{self.unit.unit_type} {self.territory} H"

    def get_dependencies(self, orders):
        # returns the move orders and support hold orders directed at this territory
        # TODO: make this function look more like Move_Order.get_dependencies
        move_orders = list(filter(lambda order: isinstance(order, Move_Order), orders))
        support_orders = list(filter(lambda order: isinstance(order, Support_Hold_Order), orders))
        dependent_orders = list(filter(lambda order: order.target == self.territory, move_orders + support_orders))
        return dependent_orders

    def resolve(self, debug_tabs):
        # determine dependencies
        adjacent_orders = self.get_adjacent_orders()
        self.dependencies = self.get_dependencies(adjacent_orders)

        super().resolve(debug_tabs)

        if self.succeeded:
            self.handle_success(debug_tabs)
        else:
            self.handle_failure(debug_tabs)

    def handle_success(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit at {self.territory.name} successfully held!")

    def handle_failure(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit at {self.territory.name} was dislodged!")
        self.unit.dislodge()


class Move_Order(Order):
    def __init__(self, game_map, unit, target):
        Order.__init__(self, game_map, unit)
        self.target = target
        self.target.add_claim(self)
        self.convoy_failed = False
        self.strength = 1

    def __str__(self):
        return f"{self.unit.unit_type} {self.territory} => {self.target}"

    def get_dependencies(self, orders):
        # returns the move orders whose targets match self.target
        # and any orders whose territorys match self.target
        def is_relevant(order):
            if isinstance(order, Move_Order):
                if order.target == self.target:
                    return True
            elif isinstance(order, Support_Move_Order):
                if order.move_target == self.target and order.move_origin == self.territory:
                    return True
            elif order.territory == self.target:
                return True
            return False
        dependencies = [order for order in orders if is_relevant(order)]
        return dependencies

    def resolve(self, debug_tabs):
        # resolve this order, checking dependencies

        # determine dependencies
        adjacent_orders = self.get_adjacent_orders()
        self.dependencies = self.get_dependencies(adjacent_orders)

        # resolve recursively
        super().resolve(debug_tabs)

        if self.succeeded:
            self.handle_success(debug_tabs)
        else:
            self.handle_failure(debug_tabs)
    
    def handle_success(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit at {self.territory.name} successfully moved to {self.target.name}!")
        self.unit.move_to(self.target)
    
    def handle_failure(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit at {self.territory.name} failed to move to {self.target.name}!")


class Support_Order(Order): # should not be directly instanced
    def __init__(self, game_map, unit):
        Order.__init__(self, game_map, unit)

    def __str__(self):
        return f"{self.unit.unit_type} {self.territory} S {self.supported_order}"

    def get_dependencies(self, orders):
        # return move orders whose targets match self.territory
        def is_relevant(order):
            if isinstance(order, Move_Order):
                if (order.target == self.territory):
                    return True
            return False
        dependencies = [order for order in orders if is_relevant(order)]
        return dependencies

    def resolve(self, debug_tabs):
        # resolve this order, checking dependencies

        # determine dependencies
        adjacent_orders = self.get_adjacent_orders()
        self.dependencies = self.get_dependencies(adjacent_orders)

        # resolve recursively
        super().resolve(debug_tabs)

        # this is a support order, so it will fail if any deps succeed
        if any([dep is dep for dep in self.dependencies]):
            self.succeeded = False
        else: # Note: this will result in success if there are no deps
            self.succeeded = True

        if self.succeeded:
            self.handle_success(debug_tabs)
        else:
            self.handle_failure(debug_tabs)
        self.state = RESOLVED


class Support_Hold_Order(Support_Order):
    def __init__(self, game_map, unit, target):
        Support_Order.__init__(self, game_map, unit)
        self.target = target
        self.supported_order = self.game_map.get_order_at(self.target)
        if not isinstance(self.supported_order, Hold_Order):
            self.state = RESOLVED
            self.succeeded = False

    def handle_success(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit at {self.territory.name} successfully support-held the unit in {self.target.name}")
        self.supported_order.strength += 1

    def handle_failure(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit at {self.territory.name} could not support-hold the unit in {self.target.name}")


class Support_Move_Order(Support_Order):
    def __init__(self, game_map, unit, move_target, move_origin):
        Support_Order.__init__(self, game_map, unit)
        self.move_target = move_target
        self.move_origin = move_origin
        self.supported_order = self.game_map.get_order_at(self.move_origin)
        if not isinstance(self.supported_order, Move_Order):
            self.state = RESOLVED
            self.succeeded = False
            

    def handle_success(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit in {self.territory.name} successfully support-moved the unit in {self.move_origin.name} to {self.move_target.name}!")
        self.supported_order.strength += 1

    def handle_failure(self, debug_tabs):
        print("\t"*debug_tabs+f"Unit in {self.territory.name} could not support-move the unit in {self.move_origin.name} to {self.move_target.name}!")


class Convoy_Order(Order):
    def __init__(self, game_map, unit, army_target, army_origin):
        Order.__init__(self, game_map, unit)
        self.army_target = army_target
        self.army_origin = army_origin
