from orders import Hold_Order, Move_Order

class Territory:
    def __init__(self, name, neighbors=list()):
        self.name = name
        self.neighbors = neighbors
        self.claims = []
        self.unit = None

    def add_claim(self, order):
        self.claims.append(order)

    def resolve_conflict(self):
        # find strongest claim
        claim_strengths = [claim.strength for claim in self.claims]
        strongest_strength = max(claim_strengths)
        strongest = claim_strengths[claim_strengths.index(strongest_strength)]

        # check for challengers
        unchallenged = True
        for strength in claim_strengths:
            # check for a tie
            if strength == strongest_strength:
                unchallenged = False
                break
        
        # if unchallenged, the strongest claim wins
        # else, there is a standoff and nothing changes
        # TODO: add nationality exceptions (i.e. France cannot dislodge or help dislodge a French unit)
        if unchallenged:
            strongest.succeeds = True
            for claim in self.claims:
                if not claim is strongest:
                    claim.succeeds = False

            # if the strongest was a move order, dislodge the holding unit (if any) and replace
            # with the strongest unit
            if isinstance(strongest, Move_Order) and self.unit != None:
                self.unit.dislodge()
                strongest.unit.move_to(self)
        else:
            for claim in self.claims:
                claim.succeeds = False