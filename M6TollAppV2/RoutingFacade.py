
'''

Module to delegate routing requests from the user interface.

Due to the (limited RAM/disk) memory available in production, handling 
a routing request requires the marshalling of various classes. The
purpose of this module is to take this job away from the UI controller.
 
'''

from DataStore       import AWS_S3DataStore
from GraphRepository import GraphRepository
from DataStructures  import GISEdge, CompositeGraph
from algorithms      import 
from gis             import shortestPath2

findRoute ( X1, Y1, X2, Y2 ):

    '''

    Find a route between Two Points.  This involves:  

    1. Find the closest road to start/end locations
    2. Ensure that there is a complete network between
       the two points
    3. Do a routing search
    4  Return Distance, Time, GIS route (MULTILINESTRING)
       (as  JSON)

    '''

    graphRepositoryRef = GraphRepository.getGraphRepository ()

    # identify the roads 
    fromTile = Locator.getTileFromCoords ( X1, Y1 )

    if toTile not in graphRepositoryRef:
        toTileGraph = AWS_S3DataStore.loadEdgeGraphForTile ( toTile ) 
        graphRepositoryRef [toTile] = toTileGraph

    fromEdge = Locator.closestEdgeInGraph ( X1, Y1, graphRepositoryRef[fromTile]   )


    toTile = Locator.getTileFromCoords ( X2, Y2 )
    if fromTile not in graphRepositoryRef:
        toTileGraph = AWS_S3DataStore.loadEdgeGraphForTile ( fromTile ) 
        graphRepositoryRef [fromTile] = toTileGraph

    fromEdge = Locator.closestEdgeInGraph ( X1, Y1, graphRepositoryRef[fromTile]   )

    tileSet = Locator.getTileBoundingSet ( X1, Y1, X2, Y2 )

    if len ( tileSet ) + len ( graphRepositoryRef ) > 8:
        print "Memory allowance exceeded"
        #TODO 
        return 

    for aTile in tileSet:
        if aTile not in graphRepositoryRef:
            G = self.TestDatastore.loadEdgeGraphForTile ( t )
            graphRepositoryRef [t] = G

     
    cg = CompositeGraph ( graphRepositoryRef )

    resList = shortestPath ( cg , fromEdge.sourceNode, toEdge.targetNode)



