
'''

This module is responsible for caching all sub Graphs in 
the program.

Rather than instantiate GraphCache directly use getGraphCache ()
to access the singleton.

'''

from gis import Tile
from apperror import AppError


def getGraphRepository ():
    pass

def setGraphRepository (inRepository):
    pass

class GraphRepository (dict):

    '''
    A dictionary of geographical graphs indexed by the string given
    by gis.Tile.getID ()

    The repository caches by default but can be trimmed to all but the 
    most essential and used tiles.

    It is not the job of the repository to seek out requested tiles not 
    in it.  It is the job of the RoutingFacade to poll it and then set 
    things up correctly.  However, an AppError will be thrown if a 
    missing subGraph is requested.

    '''

    def __init__ (self, lstImmutableTiles ):

        '''
        Add a list of Tiles that should be preserved when the 
        cache is refreshed.

        Do not initialize with a costly set of new graphs. A 
        Factory class will add the initial graphs.

        Note: cannot construct this with GraphRepository ( [] ) 
        unless __init__ is upgraded.

        '''

        self.lstImmutableTiles = [str(st) for st in lstImmutableTiles]
        self.accessFrequency = {}


    def cacheSize ():

        '''
        Currently returns the number of tiles.
  
        May be modified to reflect the actual memory overhead of each tile.
        '''

        return len ( self )
 
    def __getitem__(self, key):

        '''
        Handle  case in which a Tile OBJECT is used 
        Also increment the frequency counter for this tile.

        '''

        keyStr = str (key ) # key might be a Tile object

        try:
            val = dict.__getitem__(self, keyStr )
        except KeyError as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'GraphRepository', \
                            'Tile with key: %s not found in GraphRepository' %(keyStr), e )

        if keyStr in self.accessFrequency:
           self.accessFrequency [keyStr] = self.accessFrequency [keyStr] + 1
        else:
           self.accessFrequency [keyStr] = 1
        return val

    def __setitem__(self, key, val):

        '''
        Anticipate that the key may be a Tile object
        '''

        dict.__setitem__(self, str(key), val)
        self.accessFrequency.setdefault ( str(key) , 0 ) 

    def __delitem__(self, key):
        keyStr = str (key)
        self.accessFrequency.pop ( keyStr, None)
        return dict.__delitem__(self, self.__keytransform__(keyStr))

    def trim (self, maxTiles):

        '''

        Trim the cache back down to size, by removing the 
        least used tiles.

        '''

        numTilesToKeep = len ( self.lstImmutableTiles )

        if ( maxTiles < numTilesToKeep) : 
            return

        availList = [(self.accessFrequency[aKey],aKey,)  \
                    for aKey in self if aKey not in self.lstImmutableTiles  ]

        sortedKeys = sorted ( availList , reverse=True  ) 

        while ( numTilesToKeep +  len ( sortedKeys ) > maxTiles ):

            print (sortedKeys)
            poppedKey = sortedKeys.pop () [1]
            self.pop ( poppedKey, None )
 
class GraphRepositoryFactory (object):

    def create (self, objDataStore, lstCoreTiles):
        '''
        @objDataStore   instance of a DataStore.GenericDataStore subclass

        @lstCoreTiles   list of gis.Tile
 
        '''
 
        gr = GraphRepository(lstCoreTiles  )

        for thisTile in lstCoreTiles:
            thisGraph = objDataStore.loadEdgeGraphForTile ( str ( thisTile ) )

            gr [ thisTile ] = thisGraph

        return gr


