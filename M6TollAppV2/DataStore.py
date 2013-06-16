
'''

This module creates the Graph/network used for routing.  

There are a number of potential sources of Edges/roads and therefore different subclasses 
of the abstract class DataStore can be implemented.

Currently this app is hosted on Heroku without payment privileges. As a result database access is
restricted to 10,000 rows.  Given that this app requires over 200,000 rows S3 is being used for 
all data.

Classes in this module are:

- GenericDataStore 

- AWS_S3DataStore

- TestDataStore

- FileDataStore

'''

from DataStructures import GISEdge
from gis import Tile 

from apperror import AppError
import os

from boto.s3.key import Key
from boto.exception import AWSConnectionError
from boto.s3.connection import S3Connection

class GenericDataStore (object):

    '''

    Abstract base class which provides one function loadEdgeGraphForTile (str).
  
    This function creates a graph from a list of strings, the required format of 
    which is defined below.

    Subclasses will be need to implement the method _getStringList (self, thisTile)

    Note that there is not closedown () function (for connections, file handles etc) 
    BUT subclasses are expected to manage and reuse connections while ensuring that 
    they have not gone stale.

    '''

    def _getStringList (self, thisTile):

        '''

        Virtual method - override this in subclasses

        A list of strings in well known format is expected.

        see docstr in self.createEdgeFromLine() for a defition of the
        input string list 
         
        '''
    
        pass 


    def _createEdgeFromLine (self, lineStr):

        '''
        @inLine definition

        FromNode|ToNode|costFromTo|costToFrom|dist_km|road speed_kmh|(is_toll?)f/t|
        well known text (WKT of geometry|mid-point of road|mid point longitude|mid-point
        latitude

        e.g.        
        1911086|1911202|0.0011870678|0.0011870678|0.083094746|70|f|LINESTRING(-702231.87
        9109461 6431264.28019654,-702291.746731609 6431378.7559089)|POINT(-6.3085252 49.
        9135723)|-6|50

        Returns two Edge objects - from a-b and reverse Edge from b-a 

        '''

        cols = lineStr.replace('\n','').split ("|")
        source     = str(cols [0])
        target     = str(cols [1])

        edgeID     = str (source) + "-" + str (target)
        costHRS    = float (cols [2])
        costHRSRev = float (cols [3])
        km         = float (cols [4])

        if cols[6] == 't':
            isToll  = True
        else:
            isToll  = False

        wktGM      = cols [7]  # e.g. LINESTRING(-3.04 53.8,-3.047 53.81)
        centroidWKT= cols [8] # e.g. POINT(-3.0460 53.81371)

        thisEdge   = GISEdge ( edgeID, source, target, wktGM , float (km), 
                               costHRS, centroidWKT , isToll) 

        return thisEdge 


    def loadEdgeGraphForTile (self, thisTile):

        '''

        A graph G is defined so:
 
        G = { nodeA:  { nodeB : cost_A-B, nodeC: cost_A-C },
              nodeB:  { nodeA : cost_B-A                  },
              nodeC:  { nodeC : cost_C-A                  }
            }

        where cost_X_Y is in an instance of DataStructures.Edge 
 
        The graph created here will be a subclass of:
        - dict 
        - gis.Tile

        '''

        try:

            strList = self._getStringList ( thisTile )

            graph = {}

            for thisLine in strList:

                thisEdge = self._createEdgeFromLine (thisLine)

                # note, do not implement reverse costs/Edges at this
                # stage, to reduce memory requirement

                graph.setdefault ( thisEdge.sourceNode, {} ) 
                graph[thisEdge.sourceNode][thisEdge.targetNode] = thisEdge

                graph.setdefault ( thisEdge.targetNode, {} ) 
                graph[thisEdge.targetNode][thisEdge.sourceNode] = thisEdge

        except (AWSConnectionError, Exception) as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )

            raise AppError (utils.timestampStr (), 'DataStore', \
                            'loadEdgeGraphForTile',   e )

        return graph 


class AWS_S3DataStore (GenericDataStore):
   
    '''

    Subclass of GenericDatastore. Uses an S3 store in which every tile is a 
    bucket.  Buckets contain a block of text in which Edges are separated  
    from each other by newline characters.
 
    '''

    def __init__ (self):
        self.bucketPrefix = "caliguladrive.graphs"

    def _getKeyNameFromTile (self, aTile ):
        return self.bucketPrefix + '.' + aTile.getID ()
    
    def _getStringList (self, thisTile):
 
        conn = self._getS3Connection ()

        bucketRef = None
        keyID = None 

        try:
            bucketRef =conn.get_bucket ( self.bucketPrefix );
        except (AWSConnectionError, Exception) as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            errStr = 'Opening key %s' %( keyID )
            raise AppError (utils.timestampStr (), 'DataStore', errStr,   e )

        strEdges = None
        tileID = thisTile.getID ()
        keyRef = None

        try:
            keyRef = bucketRef.get_key ( thisTile.getID ())
            strEdges = keyRef.get_contents_as_string() 
        except (AWSConnectionError, Exception) as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            errStr = 'Reading bucket key: %s' %( tileID )
            raise AppError (utils.timestampStr (), 'DataStore', errStr,   e )

        resultList = []
        someLines = strEdges.split ('\n')
        listLen = len ( someLines )
        count = 0

        while (len ( someLines ) > 0 ):
            aLine = someLines.pop ()
            if len (aLine ) > 0:
                resultList.append ( aLine )

        conn.close ()

        return resultList

    def _getS3Connection (self):


        if 'AWS_ACCESS_KEY_ID' in os.environ:
            AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
        else :
            errStr ="AWS_ACCESS_KEY_ID not set"
            raise AppError (utils.timestampStr (), 'DataStore', errStr,   '' )

        if 'AWS_SECRET_ACCESS_KEY' in os.environ:
            AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
        else :
            errStr ="AWS_SECRET_ACCESS_KEY not set"
            raise AppError (utils.timestampStr (), 'DataStore', errStr,   '' )

        try:
            conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

        except (AWSConnectionError, Exception) as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'DataStore', 'creating AWS connection',   e )
        else:
            return conn

class TestDataStore (GenericDataStore):

    '''

    Class for testing GenericDatastore.  
    Add Edge Strings in a controlled manner using addEdgeString ()

    '''

    def __init__ (self):
        self.strList = []
 
    def addEdgeString (self, inString ):
        self.strList.append ( inString )
    
    def _getStringList (self, thisTile):

        return self.strList

import math

class FileDataStore (GenericDataStore):

    '''

    Utility class for testing program without going online

    '''

    def __init__ (self, filePath, hasHeader=False):
        self.filePath = filePath
        self.hasHeader= hasHeader
   
    def _getStringList (self, thisTile):

        '''
        Search for lines in the file that are in Tile thisTile
        return a list of those matched lines.
        '''

        lstLines = []

        try:

           fs = open ( self.filePath, 'r' )

           if (self.hasHeader): 
               fs.readline ()

           allLines = fs.readlines ()

           for thisLine in allLines:

#               print thisLine

               cols = thisLine.split ("|")
               centroidWKT= cols [8]

               # centroidWKT is like "POINT (0.2343 0.2332432)"
               tmpList = centroidWKT.replace ('POINT(','' ).replace ( ')','' ).split (" ")
               X     = float (tmpList[0] )
               Y     = float (tmpList[1] )

               # Find the integer "floor" value of x & y co-ordinates
               xVal = int (math.floor ( X ) )
               yVal = int (math.floor ( Y ) )

               if ( Tile ( xVal , yVal ) == thisTile  ):
                   lstLines.append ( thisLine )

           fs.close ()

        except IOError as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'FileDataStore', 'open/read file',   e )
 
        return lstLines


