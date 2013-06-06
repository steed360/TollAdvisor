
'''

Module to assist with the basic spatial requirements of the app.

The following classes are defined:

Tile          :  Reference to a geographical area. Useful in spatially organizing a 
                 large spatial dataset (into separate 'tiles'). A 2 dimensional 
                 co-ordinate system is assumed, but unspecified. 

Locator       :  Contains logic for matching co-ordinates to Tiles and for matching
                 a co-ordinate to TileFeature feature within a Tile.

Also, module functions:

_pythagorasDistance               

MergeWKT          Adds two or more LINESTRINGs together to produce a MULTILINESTRING

'''
import math

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


    def getX (self):
        return self.x1

    def getY (self):
        return self.y1

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


class Locator ():

    '''
    
    Very basic GIS-ish search operations
    
    ''' 

    @classmethod
    def getTileFromCoords (cls, X,Y):
        '''
        Find the Tile that contains the Point (X,Y).

        Because each Tile is identified by it's bottom 
        and left-most points, this is simple.
        '''

        xVal = 0
        yVal = 0

        xVal = int (math.floor ( X ) )
        yVal = int (math.floor ( Y ) )

        return Tile ( xVal , yVal)

    @classmethod
    def closestEdgeInGraph (cls, X, Y, aGraph ):

        '''
        @aTile            gis.Tile
        @aGraph           Graph -see DataStructures 
                          header docs 
                          e.g. G = { 'a':{'b':10},{'c':5} etc }
    
        '''

        if len ( aGraph ) == 0:
           raise AppError (utils.timestampStr (), 'gis.Locator.locateEdgeInGraph', \
                        'Received  empty graph for Tile: %s' %(aTile.getID() ), None  )

        maxDist = 10000000000
        closestEdge = None

        for i in aGraph.iterkeys ():
            for thisEdge in (aGraph[i]).itervalues ():

                dist = _pythagorasDistance ( X, Y , \
                                    thisEdge.CentroidX, \
                                    thisEdge.CentroidY )

                if dist < maxDist:
                    maxDist = dist
                    closestEdge = thisEdge

        if (not closestEdge ):
            raise AppError (utils.timestampStr (), 'gis.Locator.locateEdgeInGraph', \
                        'No match found for Tile: %s' %(aTile.getID() ), None  )
                
        return closestEdge

    @classmethod
    def getTileBoundingSet (cls, X1, Y1, X2, Y2 ):
    
        '''

        Bounding Set refers the set of Tile Graphs needed to 
        route between point 1 and point 2.


        '''

        # Return a limited set of Edges likely to form a between 
        # the two points

        t1 = Locator.getTileFromCoords (X1, Y1)
        t2 = Locator.getTileFromCoords (X2, Y2)
 

        minX = min ( t1.getX(), t2.getX() )
        maxX = max ( t1.getX(), t2.getX() )

        minY = min ( t1.getY(), t2.getY() )
        maxY = max ( t1.getY(), t2.getY() )

        xRange = range ( int (minX), int(maxX) + 1 )
        yRange = range ( int (minY), int(maxY) + 1 )

        resultList =[]
        for x in xRange:
            for y in yRange:
                print "yo-" + str ( Tile (x,y) )
                resultList += [Tile (x,y)]

        return resultList

def _pythagorasDistance ( X1, Y1, X2, Y2 ):
 
    side1 = abs( float (Y2) - float (Y1)  )
    side2 = abs( float (X2) - float (X1)  )

    return math.sqrt ( math.pow ( side1, 2 ) + math.pow ( side2, 2 ) ) 



def mergeWKT ( firstWKT , secondWKT ): 
  def extractCoords( inWKT ):

    if inWKT[0:len('LINESTRING')] == "LINESTRING":
      return inWKT [ len ('LINESTRING') : ]

    if inWKT[0:len('MULTILINESTRING(') ] == "MULTILINESTRING(":
      return inWKT [ len ("MULTILINESTRING(") : -1 ]

  if firstWKT  == None: return secondWKT
  if secondWKT == None: return firstWKT

  return  "MULTILINESTRING(" + \
           extractCoords ( secondWKT)  + ',' + \
           extractCoords (firstWKT) + ")"


