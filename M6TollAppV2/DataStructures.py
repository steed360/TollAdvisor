
'''

Define data structures required for the shortest path algorithms.
The following classes are defined:

The key structure in this routing app is a graph G, defined as   


    G = { nodeA:  { nodeB : cost_A-B, nodeC: cost_A-C },
          nodeB:  { nodeA : cost_B-A                  },
          nodeC:  { nodeC : cost_C-A                  }
        }


- EdgeCost            Abstract base class returning a comparable value 
                      of its travel cost. I.E replaces cost_A-C in the above
                      graph example

- GISEdge             Subclass of EdgeCost.  Adds information for drawing the 
                      Edge. Included up front due at a cost of memory overhead
                      due to the cost of fetching this data over the network.

- priority_dict       Subclass of dictionary providing a fast ordering on each   
                      (value) item in the dictionary
                      

- d_priority_dict     Destructive PriorityDict. Items are iterated in ascending value
                      order. At the end of each iteration the selected key/value item 
                      is deleted.

- CompositeGraph      Provides key value access to a set of different sub graphs.
                      Caters for the routing algorithm which expects a single graph.
                      Allows for the fact that this app has memory restrictions on the 
                      number of graphs permiited in memory at one time. 
                      Works closely with  GraphRepository.GraphRepository.

Hence with all these tweaks the final graph structure is structured along these lines:

    CompositeGraph   = [{ 'a':  { 'b' : GISEdge(A-B), 'c': GISEdge(A-C)  },
                          'b':  { 'a' : GISEdge (B-A)                      },
                          'c':  { 'a' : GISEdge (B-A)                      },

                        }, 
                        { 'c':  { 'd' : GISEdge (D-E) },
                          'd':  { 'c' : GISEdge (E-D)                      },
                        }]

Note that nodeC appears in both graphs. Important, this should hold:
CompositeGraph ['c'] = { 'a' : COST1 , 'd': COST2  }

'''

from heapq import heapify, heappush, heappop
from GraphRepository import GraphRepository
from apperror import AppError
import utils


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

    def __str__(self):
        return "Edge from %s to %s at cost %s " %(self.sourceNode,self.targetNode,\
                                                  self.edgeCost )


# source/credits:
# http://code.activestate.com/recipes/522995-priority-dict-a-priority-queue-with-updatable-prio/?c=14610

from heapq import heapify, heappush, heappop

class priority_dict(dict):

    """Dictionary that can be used as a priority queue.

    Keys of the dictionary are items to be put into the queue, and values
    are their respective priorities. All dictionary methods work as expected.
    The advantage over a standard heapq-based priority queue is
    that priorities of items can be efficiently updated (amortized O(1))
    using code as 'thedict[item] = new_priority.'

    The 'smallest' method can be used to return the object with lowest
    priority, and 'pop_smallest' also removes it.

    The 'sorted_iter' method provides a destructive sorted iterator.
    """
    
    def __init__(self, *args, **kwargs):
        super(priority_dict, self).__init__(*args, **kwargs)
        self._rebuild_heap()

    def _rebuild_heap(self):
        self._heap = [(v, k) for k, v in self.iteritems()]
        heapify(self._heap)

    def smallest(self):
        """Return the item with the lowest priority.

        Raises IndexError if the object is empty.
        """
        
        heap = self._heap
        v, k = heap[0]
        while k not in self or self[k] != v:
            heappop(heap)
            v, k = heap[0]
        return k

    def pop_smallest(self):
        """Return the item with the lowest priority and remove it.

        Raises IndexError if the object is empty.
        """
        
        heap = self._heap
        v, k = heappop(heap)
        while k not in self or self[k] != v:
            v, k = heappop(heap)
        del self[k]
        return k

    def __setitem__(self, key, val):
        # We are not going to remove the previous value from the heap,
        # since this would have a cost O(n).
        
        super(priority_dict, self).__setitem__(key, val)
        
        if len(self._heap) < 2 * len(self):
            heappush(self._heap, (val, key))
        else:
            # When the heap grows larger than 2 * len(self), we rebuild it
            # from scratch to avoid wasting too much memory.
            self._rebuild_heap()

    def setdefault(self, key, val):
        if key not in self:
            self[key] = val
            return val
        return self[key]

    def update(self, *args, **kwargs):
        # Reimplementing dict.update is tricky -- see e.g.
        # http://mail.python.org/pipermail/python-ideas/2007-May/000744.html
        # We just rebuild the heap from scratch after passing to super.
        
        super(priority_dict, self).update(*args, **kwargs)
        self._rebuild_heap()


class d_priority_dict (priority_dict):

    '''
    Destructive priority dictionary.  Provides an iterator across dictionary keys
    which self-sort by dictionary values.  The last accessed key/value is deleted 
    at the end of each iteration.

    '''
    def __iter__(self):
        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]
        return iterfn()


class CompositeGraph (dict):
    
    '''
    This is a composite set of dictionaries but it must provide access
    to a value via a key seamlessley.

    E.g. Graph 1 may represent the area covered by Tile 1
         - and contain the key A
         Graph 2 may represent the area covered by Tile 2
         - and contain the key B
    
         CD is a 

    Receives a list of dictionaries and then provides access to the 
    keys of each sub dictionary as though the key/value pair belonged
    to this dictionary.

    Note : many standard dictionary functions are not supported.  
    In particular this structure does not provide (a correct) iterator.

    '''

    def __init__ (self, GraphRepository ):

        '''
        Tightly bind this structure to the GraphRepository.
        Consider looser linking.
        '''
   
        self.GraphRepository = GraphRepository

    def __getitem__(self, key):

        '''
        Superficially this needs to get the value matching the key in 
        which every sub graph is being accessed. 

        Matters are slightly more complicated. Consider a basic 
        graph
  
        G = { nodeA:  { nodeB : cost_A-B, nodeC: cost_A-C },
              nodeB:  { nodeA : cost_B-A                  },
              nodeC:  { nodeC : cost_C-A                  }
             }

        1. If CompositeGraph replaces G then "values" are 
           in fact sub-dictionaries

        2. It is possible for two graphs to contain 'from' nodes
           that link to the same 'to node. To handle this, it is
           necessary to return a graph that includes the values of
           all child graphs.

        '''
 
        lstAvailableGraphs = []
        lstAvailableGraphs = self.GraphRepository.getGraphs ()

        lstResults = []

        for eachGraph in lstAvailableGraphs:
            # create a list of (key,val) tuples
            if key in eachGraph:

                dictResult = eachGraph[key]
                lstResults =lstResults + \
                           [(akey,val) for akey,val in dictResult.iteritems()]

        if len (lstResults) == 0:
            raise AppError (utils.timestampStr (), 'DataStructures.DynamicGraph', \
                            'Failed to find key "%s" in CompositeGraph:' %(key), 'AppError' )

        # note: the next line will flatten out any duplicates.
        return dict ( lstResults ) # generate dict from key/val pairs

    def __setitem__(self, key, val):
        '''
        Not implemented
        '''
        pass
 
