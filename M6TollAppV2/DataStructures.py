
'''

Define data structures required for the shortest path algorithms.
The following classes are defined:

- EdgeCost            Abstract base class returning a comparable value 
                      of its travel cost

- GISEdge             Subclass of EdgeCost.  Adds information for drawing the 
                      Edge. Included up front due at a cost of memory overhead
                      due to the cost of fetching this data over the network.

- PriorityDict        Subclass of dictionary performing ordered iteration 
                      on value of it's contents  

- DestructivePriorityDict        
                      Subclass of PriorityDict that removes each at the end of each
                      each iteration loop.  Permit efficient simulation of searching
                      through a 'frontier list' in the Dijkstra routing search

- DynamicGraph        


'''


class EdgeCost (object):

    '''

    An 'edge cost' defines the cost of travel between nodes A and B

    This comparable implementation fits into the algorithms.shortestPath 
    routine.

    This should be treated as an abstract base class.  If a super class 
    serves no additional function - i.e. there are no other edge 
    attributes that need to be represented - then it would be far more
    efficient to replace this class with a numeric cost value in the 
    algorithm.
    

    '''

    def __init__(self, inCost = 100000):
        self.edgeCost = float (inCost)
    
    def setCost (self, inCost):
        self.edgeCost= float (inCost)

    def getCost (self):
        return self.edgeCost

    def __gt__(self, other):
        return self.edgeCost > other.edgeCost
    def __lt__(self, other):
        return self.edgeCost < other.edgeCost
    def __eq__(self, other):
        return self.edgeCost == other.edgeCost  
    def __ge__(self, other):
        return self.edgeCost >= other.edgeCost
    def __le__(self, other):
        return self.edgeCost <= other.edgeCost 
    def __str__(self):
        return str ( getCost (self) )


class GISEdge (EdgeCost):

    ''' 

    This class contains the geometry and cost of a single direction 
    roadlink.

    The class is an Observer of the RoutingContext, event from
    which cause the class to alter the cost appropriately. 

    For example, if the RoutingContext is to avoid tolls, the 
    cost of a tolled link will read as infinite.

    '''

    def __init__ (self, edgeID = None,      sourceNode = None, 
                        targetNode = None,  WKT = None,        
                        lengthKM = 0,    edgeCost = 0, 
                        centroidWKT = "", isToll = False ):

        EdgeCost.__init__(self, edgeCost)

        self.edgeID        = edgeID
        self.originalCost  = edgeCost 
        self.sourceNode    = str(sourceNode)
        self.targetNode    = str(targetNode)
        self.WKT           = WKT       # Well known text (Linestring)
        self.lengthKM      = float (lengthKM)
  
        # centroidWKT is like "POINT (0.2343 0.2332432)"
        tmpList = centroidWKT.replace ('POINT(','' ).replace ( ')','' ).split (" ")
        self.CentroidX     = float (tmpList[0] )
        self.CentroidY     = float (tmpList[1] )

        self.isToll = isToll


