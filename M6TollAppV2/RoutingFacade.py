
'''

Module to delegate routing requests from the user interface.

Due to the (limited RAM/disk) memory available in production, handling 
a routing request requires the marshalling of various classes. The
purpose of this module is to take this job away from the UI controller.
 
'''

from DataStore       import AWS_S3DataStore
from GraphRepository import GraphRepository
from DataStructures  import GISEdge, CompositeGraph
from algorithms      import shortestPath2
from gis             import Locator



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

    fromEdge = Locator.closestEdgeInGraph ( X2, Y2, graphRepositoryRef[fromTile]   )

    tileSet = Locator.getTileBoundingSet ( X1, Y1, X2, Y2 )

    if len ( tileSet ) + len ( graphRepositoryRef ) > 8:
        print "Memory allowance exceeded"
        #TODO 
        return 

    for aTile in tileSet:
        if aTile not in graphRepositoryRef:
            G = AWS_S3DataStore.loadEdgeGraphForTile ( t )
            graphRepositoryRef [t] = G
    
    cg = CompositeGraph ( graphRepositoryRef )

    resList = shortestPath ( cg , fromEdge.sourceNode, toEdge.targetNode)

    return  _getJSONResultFromNodesList ( resList )



def _getJSONResultFromNodesList (edgeList):

    import json

    '''

    @ edgeList : list  DataStructures.GISEdge

    returns a JSON result with keys : 'WKT', 'TIME_HRS', 'DIST_KM'

    ''' 
    
    timeHRS = 0
    distKM  = 0
    lastNode= None
    WKT     = None  # Well known text repr of a geometry

    for thisEdge in edgeList:

        timeHRS += thisEdge.getCost ()
        distKM  += thisEdge.lengthKM
        WKT = gis._mergeWKT (WKT, thisEdge.WKT )                 

    print "----------------"
    print "Time : " + str  ( timeHRS) 
    print "----------------"
    print "DIST : " + str  ( distKM) 
    print "----------------"

    resultDict = {}
    resultDict ['WKT'] = WKT
    resultDict ['TIME_HRS'] = timeHRS
    resultDict ['DIST_KM'] = distKM

    return json.dumps ( resultDict )  


