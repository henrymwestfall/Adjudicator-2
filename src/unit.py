class Unit:
    def __init__(self, unit_type, territory):
        self.unit_type = unit_type
        self.nationality = "Neutral" # TODO: add nationalities
        self.territory = territory
        self.territory.unit = self
        self.birthplace = territory # serves no function, but could be fun to look at
        self.order = None

    def move_to(self, territory):
        self.territory = territory
        self.territory.unit = self

    def dislodge(self):
        # TODO: dislodgement
        pass