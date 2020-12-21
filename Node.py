# Code taken from https://www.annytab.com/a-star-search-algorithm-in-python/
class Node:
    # Initialize the class
    def __init__(self, position:(), parent:(), moveMade:()):
        self.position = position
        self.parent = parent
        self.g = 0 # Distance from start node
        self.h = 0 # Distance to goal node
        self.f = 0 # Total cost
        self.moveMade = moveMade
    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position
    # Sort nodes
    def __lt__(self, other):
         return self.f < other.f
    # Print node
    def __repr__(self):
        return ('({0},{1})'.format(self.position, self.f))