from orders import Hold_Order, Move_Order, RESOLVED


class Territory:
    def __init__(self, name, neighbors=list()):
        self.name = name
        self.neighbors = neighbors
        self.claims = []
        self.unit = None

        self.sc = False # supply center
        self.hsc = False # home supply center
        self.terrain = "land"

    def __str__(self):
        return self.name

    def add_claim(self, order):
        self.claims.append(order)

    def resolve_conflict(self):
        # find strongest claim
        claim_strengths = [claim.strength for claim in self.claims]
        strongest_strength = max(claim_strengths)
        strongest = self.claims[claim_strengths.index(strongest_strength)]

        # check for challengers
        unchallenged = claim_strengths.count(strongest_strength) == 1
        
        # if unchallenged, the strongest claim wins
        # else, there is a standoff and nothing changes
        # TODO: add nationality exceptions (i.e. France cannot dislodge or help dislodge a French unit)
        if unchallenged:
            strongest.succeeded = True
            for claim in self.claims:
                if not claim is strongest:
                    claim.succeeded = False
        else:
            for claim in self.claims:
                if isinstance(claim, Hold_Order):
                    claim.succeeded = True
                else:
                    claim.succeeded = False
                claim.state = RESOLVED