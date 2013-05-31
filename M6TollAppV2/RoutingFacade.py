
'''

Module to delegate routing requests from the user interface.

Due to the (limited RAM/disk) memory available in production, handling 
a routing request requires the marshalling of various classes. The
purpose of this module is to take this job away from the UI controller.
 
'''

from DataStore import AWS_S3DataStore
from GraphRepository import GraphRepository
from DataStructures import GISEdge
from gis import Locator

findRoute ( X1, Y1, X2, Y2 ):

    '''

    Find a route between Two Points

    Return Distance, Time, GIS route (MULTILINESTRING)
    (as  JSON)

    '''

    graphRepositoryRef = GraphRepository.getGraphRepository ()

    fromTile = Locator.getTileFromCoords ( X1, Y1 )
    if fromTile not in graphRepositoryRef:
        fromTileGraph = AWS_S3DataStore.loadEdgeGraphForTile ( fromTile ) 

    toTile = Locator.getTileFromCoords ( X2, Y2 )
    if toTile not in graphRepositoryRef:
        toTileGraph = AWS_S3DataStore.loadEdgeGraphForTile ( toTile ) 

     
    tileSet = Locator.


