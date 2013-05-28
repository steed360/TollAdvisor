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


    def setCoords (self, x1, y1, x2=None, y2=None ):

        '''
        Allow subclasses to set co-ordinate information
        '''

        self.x1 = x1
        self.y1 = y1

    def __str__(self):
        return self.getID ()


    def __repr__(self):
        return self.getID ()

    def __hash__(self):
        return id (self.getID ())

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


t1 = Tile (1,2)
t2 = Tile (2,3)

x = str (t1) + 'xxx'

print x







