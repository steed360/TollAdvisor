
'''

Module to assist with the spatial elements of the application. The following
classes are defined:

Tile          :  Reference to a geographical area. Useful in spatially organizing a 
                 large spatial dataset (into separate 'tiles'). A 2 dimensional 
                 co-ordinate system is assumed, but unspecified. 

TODO
TileFeature   :  Provides a simple interface that should be implemented by any  
                 object that, in spatial terms, is contained within a Tile

Locator       :  Contains logic for matching co-ordinates to Tiles and for matching
                 a co-ordinate to TileFeature feature within a Tile.

Utils         :  Contains a couple of standard spatial functions likely to be found in a 
                 GIS package.

'''

class Tile ():

    '''
    A Tile defines a simple polygon within a (n unknown) co-ordinate system.

    A tile is normally a square with bottom-left and top-right points defined.
    This functionality is not yet required in this app - only the bottom left
    co-ordinate to be defined. 

    In this app, Tiles are used to spatially reference groups of roads/edges, that
    is as a basic spatial indexing system. 
    
    ''' 

    def __init__ (self, x1, y1, x2=None, y2=None ):
        self.x1 = x1
        self.y1 = y1

    def __eq__(self, other):
        '''
        A Tile is a data type, so should be comparable vs other Tiles.
        '''

        return self.x1  == other.x1 and \
               self.y1  == other.y1 


    def __str__(self):
        return self.getID ()


    def setCoords (self, x1, y1, x2=None, y2=None ):

        '''
        Allow subclasses to set co-ordinate information
        '''

        self.x1 = x1
        self.y1 = y1

    def getID (self):

        '''
        Return the String name of this tile
        '''

        def renameMinus (intVal):

            ''' AWS S3 buckets cannot have '-' in name '''

            if (int (intVal ) < 0):
                return 'm' + str (intVal)
            return str ( int (intVal) )

        if self.x1 == None or self.y1 == None:
            raise Exception ('gis.Tile Class: Tile used without co-ordinates')

        xVal = renameMinus (self.x1)
        yVal = renameMinus (self.y1)
 
        return  "%s.%s" %( xVal, yVal ) 




