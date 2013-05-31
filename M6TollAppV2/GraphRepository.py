'''

This module is responsible for caching all sub Graphs in 
the program.

Rather than instantiate GraphCache directly use getGraphCache ()
to access the singleton.

'''

from gis import Tile
from apperror import AppError


class GraphRepository (dict):

    '''
    A dictionary of geographical graphs indexed by the string given
    by gis.Tile.getID ()

    The repository caches by default but can be trimmed to all but the 
    most essential and used tiles.

    It is not the job of the repository to seek out requested tiles.
    Rather the RoutingFacade should poll the repository i.e.:
    >   tile in GraphRepository 
    If a tile is not available the RoutingFacade can use the DataStore
    to download the required tile and then add it to the Repository
    >  GraphRepository [aTile] = downloadedGraph 

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

    def getKeys (self):
        '''
        Return a list of all of the Tile (key)s currently held in the repository
        '''

        lst= []
        try:
            for key,val in self.iteritems ():
                lst.append ( key ) 
        except Exception as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'GraphRepository', \
                            'Iterating repository, at key %s:' %(key), e )

        return lst

    def getGraphs (self):

        '''
        Return a list of all of the graphs currently held in the repository
        '''

        # return self.itervalues()

        lst= []
        try:
            for key,val in self.iteritems ():
                lst.append ( val ) 
        except Exception as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'GraphRepository', \
                            'Iterating repository, at key %s:' %(key), e )

        return lst

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

            poppedKey = sortedKeys.pop () [1]
            self.pop ( poppedKey, None )

 
class GraphRepositoryFactory (object):

    def __init__(self):
        pass

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

aGraphRepository = GraphRepository ([])

def getGraphRepository (  ):
    return aGraphRepository


