import modelization.Simulation

class Test(object):
    """description of class"""
    def __init__(self, simulation):
        self.simulation = simulation
        self.G = simulation.G

    def run(self):
        pass


class TestLemmaDomination(Test):
    def __init__(self, simulation):
        return super().__init__(simulation)


    def run(self):
        for s1 in self.G.stateList:
            for s2 in self.G.stateList:
                if self.dominates(s1, s2) and s1.price > s2.price:
                    print("Exception: " + str(s1) + ", " + str(s2))

    def dominates(self, s1, s2):
        n = len(s1.tuple)
        res = True
        i = 0
        ss1 = 0
        ss2 = 0
        while res and i < n:
            ss1+=s1.tuple[i]
            ss2+=s2.tuple[i]
            res = (ss1 >= ss2)
            i+=1
        return res
