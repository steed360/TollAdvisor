
'''

Module to delegate routing requests from the user interface.

Due to the (limited RAM/disk) memory available in production, handling 
a routing request requires the marshalling of various classes. The
purpose of this module is to take this job away from the UI controller.
 
'''

from DataStore       import AWS_S3DataStore
from DataStructures  import GISEdge, CompositeGraph
from algorithms      import shortestPath2
from gis             import Locator, Tile
import gis

import GraphRepository


def findRoute ( X1, Y1, X2, Y2 ):

    '''

    Find a route between Two Points.  This involves:  

    1. Find the closest road to start/end locations
    2. Ensure that there is a complete network between
       the two points
    3. Do a routing search
    4  Return Distance, Time, GIS route (MULTILINESTRING)
       (as  JSON)

    '''

    X1 = float (X1)
    Y2 = float (Y2)

    Y1 = float (Y1)
    X2 = float (X2)

 
    print ".. Find route from %s, %s " %(X1, Y1)
    print ".. Find route to %s, %s " %(X2, Y2)

    graphRepositoryRef = GraphRepository.getGraphRepository ()
    dataStore = AWS_S3DataStore ()
    # identify the roads 
    fromTile = Locator.getTileFromCoords ( X1, Y1 )
  
    print "from tile %s" %(fromTile.getID()  )

    if fromTile.getID() not in graphRepositoryRef:
        print "Getting From Tile %s" %(fromTile.getID())
        fromTileGraph = dataStore.loadEdgeGraphForTile ( fromTile ) 
        graphRepositoryRef [fromTile] = fromTileGraph

    fromEdge = Locator.closestEdgeInGraph ( X1, Y1, graphRepositoryRef[fromTile]   )


    toTile = Locator.getTileFromCoords ( X2, Y2 )

    print ".. TO tile %s" %(toTile.getID()  )

    if toTile.getID() not in graphRepositoryRef:
        print "Getting From Tile %s" %(toTile.getID())

        toTileGraph = dataStore.loadEdgeGraphForTile ( toTile ) 
        graphRepositoryRef [toTile] = toTileGraph

    toEdge = Locator.closestEdgeInGraph ( X2, Y2, graphRepositoryRef[toTile]   )

    print "loading tileset"

    tileSet = Locator.getTileBoundingSet ( X1, Y1, X2, Y2 )

    if len ( tileSet ) + len ( graphRepositoryRef ) > 8:
        print "Memory allowance exceeded"
        #TODO 
        return 

    for aTile in tileSet:
        if  aTile.getID() not in graphRepositoryRef:
            print "getting tile: %s" %(aTile.getID() )
            G = dataStore.loadEdgeGraphForTile ( aTile )
            graphRepositoryRef [aTile] = G
    
    cg = CompositeGraph ( graphRepositoryRef )

    print "do shortest path"
    resList = shortestPath2 ( cg , fromEdge.sourceNode, toEdge.sourceNode)


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
        WKT = gis.mergeWKT (WKT, thisEdge.WKT )                 

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


