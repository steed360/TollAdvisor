
import unittest
from gis import Tile
from apperror import AppError

class TestTile (unittest.TestCase):

    ''' 
    Test the gis.Tile class
    ''' 

    def setUp(self):
        pass

    def test_getID (self):

        '''
        Test that digital co-ordinates are rationalised to 
        the bottom left corner of a tile in the simplified system

        Test that the minus does not follow the dot in the ID (s3 
        does not tolerate this).
        '''

        t =  Tile (10,20)
        self.failUnless ( t.getID () == "10.20" )

        t =  Tile (-1,20)

        self.failUnless ( t.getID () == "m-1.20" )


    def test_Compare (self):
 
        ''' 
        A tile is a data type so ensure that two tiles can be
        compared 
        '''
        t1 =  Tile (10,20)
        t2 =  Tile (-1,20)
        self.failUnless ( not t1 == t2 )

        t3 =  Tile (-1,20)
        self.failUnless ( t2 == t3 )


import DataStore

class TestTest_Datastore (unittest.TestCase):

    ''' 
    Test the GenericDatastore class
    ''' 

    def setUp(self):
        self.TestDatastore = DataStore.TestDataStore ()


        l = "1911086|1911202|0.0011870678|0.0011870678|0.083094746|70|f|"\
            "LINESTRING(-702231.879109461 6431264.28019654,-702291.746731609"\
            " 6431378.7559089)|POINT(-6.3085252 49.9135723)|-6|50"
   
        self.TestDatastore.addEdgeString ( l ) 


        l = "1911202|1892488|0.0060791424|0.0060791424|0.42553997|70|t|"\
            "LINESTRING(-635277.602517193 6457741.32494093,-634614.004768676"\
             " 6457750.93247799)|POINT(-5.70381517192721 50.0661856778543)|-6|50"

        self.TestDatastore.addEdgeString ( l ) 


    def test_StoreGraphSetup (self):

        '''
        
        Test that the important attributes from the input text string 
        are represented in the Edge classes that are created.
 
        '''

        t =  Tile (-6,50)
        G = self.TestDatastore.loadEdgeGraphForTile ( t )

        # Check length of graph
        self.failUnless ( len (G) == 3 )

        # Check distance from 1911202 - 1911086
        anEdge= G['1911202']['1911086']
        self.failUnless ( (anEdge.getCost () - 0.0011870678) < 0.00001  )

        # Check distance from 1911086 - 1911202  
        anEdge= G['1911086']['1911202']
        self.failUnless ( (anEdge.getCost () - 0.0011870678) < 0.00001  )

        # check distance from 1911202 - 1892488 is 0.0060791424
        anEdge= G['1911202']['1892488']
        self.failUnless ( (anEdge.getCost () - 0.0060791424) < 0.00001  )

        # check that node 1911202 has 2 edges
        self.failUnless (  len (G ['1911202'])  == 2)


    def test_StoreAttributes (self):

        '''
        
        Test that the important attributes from the input text string 
        are represented in the Edge classes that are created.
 
        '''

        t =  Tile (-6,50)
        G = self.TestDatastore.loadEdgeGraphForTile ( t )

        # Check that Edge class correctly holds WKT 
        anEdge= G['1911086']['1911202']
    
        wkt = "LINESTRING(-702231.879109461 6431264.28019654,-702291.746731609"\
              " 6431378.7559089)"

        self.failUnless ( anEdge.WKT == wkt )
  
        # check that Edge correctly stores centroid info  
        # POINT(-6.3085252 49.9135723)|-6|50"
  
        self.failUnless ( anEdge.CentroidX == -6.3085252 )
        self.failUnless ( anEdge.CentroidY == 49.9135723 )

        # check that length in km is stored correctly
        self.failUnless ( (anEdge.lengthKM - 0.083094746) < 0.000001 )

        # check that toll links are accurately identified
        self.failUnless ( not anEdge.isToll  )

        tollEdge = G ['1911202']['1892488']
        self.failUnless (  tollEdge.isToll )

class TestTest_AWS_S3DataStore (unittest.TestCase):

    def setUp(self):
        self.S3Datastore = DataStore.AWS_S3DataStore ()

    def _test_loadGraphFromS3(self):
        '''
        just ensure that the store can be accessed and an  
        edge is created.
        '''

        t =  Tile (-1,51)
        G = self.S3Datastore.loadEdgeGraphForTile ( t )

        self.failUnless ( len (G) > 100 )


from GraphRepository import GraphRepositoryFactory
from GraphRepository import GraphRepository

from DataStore import TestDataStore
from gis import Tile

class Test_GraphRepository_Basic (unittest.TestCase):

    def setUp(self):

        self.graph_1_1 =  {'a': 1, 'b': 2}
        self.graph_2_2 =  {'c': 3, 'd': 4}
        self.graph_3_3 =  {'j': 3, 'l': 4}
        self.graph_4_4 =  {'k': 3, 'm': 4}


    def testGRAccessing(self):

        '''
        Test setting and accessing Tiles from the Repo        
        '''

        t1 = Tile ( 1, 0 ) 
        t2 = Tile ( 1, 1 ) 
        
        GR = GraphRepository ([])
        GR[t1] = self.graph_1_1
        GR[t2] = self.graph_2_2

        self.failUnless ( GR[t1.getID()]['a'] == 1    )
        self.failUnless ( GR[t2.getID()]['c'] == 3    )

        # better not to do this
        self.failUnless ( GR[t1]['a'] == 1    )
        self.failUnless ( GR[t2]['c'] == 3    )

        # safer way
        self.failUnless ( GR.accessFrequency[ t1.getID () ] == 2 )

        self.failUnless ( t1.getID () in GR )

        notThereTile = Tile (1,100)
        try:
            print (GR [notThereTile]  )
        except AppError as ae:
           self.failUnless ( ae.args[1] == 'GraphRepository' )

        # try deleting
        poppedVal = GR.pop (t1.getID() ) 
        self.failUnless ( len (GR)==  1 ) 
        self.failUnless ( poppedVal ==  self.graph_1_1  ) 

    def testGRBasicCache(self):

        '''
        Test the basic cache in the Graph Repository
        '''

        t1 = Tile ( 1, 1 ) 
        t2 = Tile ( 2, 2 ) 
        t3 = Tile ( 5, 5 ) 
        t4 = Tile ( 6, 6 ) 
    
        immutableList = [Tile(1,1).getID(), t2  ]

        GR = GraphRepository ( immutableList )
        GR[t1] = self.graph_1_1
        GR[t2] = self.graph_2_2
        GR[t3] = self.graph_3_3
        GR[t4] = self.graph_4_4

        self.failUnless ( len (GR) == 4 ) 
  
        # trim should do nothing unless maxSize has been set
        GR.trim (4)
        self.failUnless ( len (GR) == 4 ) 


        # access t3, then t3 will be the most accessed 
        # and preserved 
        x = GR[t3]

        # but t4, should be the candidate that is discarded
        GR.trim (3)
        self.failUnless ( len (GR) == 3 ) 
        self.failUnless ( t4.getID () not in GR ) 
        self.failUnless ( t3.getID ()  in GR ) 

        GR.trim (2)

        self.failUnless ( len (GR) == 2 ) 
        self.failUnless ( t3.getID () not in GR ) 

        # this should not work because there are some 
        # immutable tiles
        GR.trim (1)

        self.failUnless ( len (GR) == 2 ) 

class Test_GraphRepositoryFactory (unittest.TestCase):

    def setUp(self):

        self.TestDataStore = DataStore.TestDataStore ()

        l = "1911086|1911202|0.0011870678|0.0011870678|0.083094746|70|f|"\
            "LINESTRING(-702231.879109461 6431264.28019654,-702291.746731609"\
            " 6431378.7559089)|POINT(-6.3085252 49.9135723)|-6|50"
   
        self.TestDataStore.addEdgeString ( l ) 
   

    def testCreate(self):

        '''
        Create a Graph repository using the DataStore
        '''

        t1  =  Tile (1 ,1)
        t2 =  Tile  (2 ,2)

        tileList = [t1, t2]     

        GRF = GraphRepositoryFactory ( ) 

        graphRepo= GRF.create (self.TestDataStore , tileList )

        self.failUnless ( len (graphRepo) == 2  ) 

        self.failUnless ( t1.getID () in graphRepo ) 
        self.failUnless ( t2.getID () in graphRepo ) 


from DataStructures import d_priority_dict
from DataStructures import EdgeCost

class Test_priority_dict (unittest.TestCase):

    def setUp(self):

         pass   

    def testpd(self):

        '''
        Check that priority_dict iterates correctly

        '''
        PD = d_priority_dict ()
        PD ['medium'] = EdgeCost ( 500.0 ) 
        PD ['high']   = EdgeCost ( 10000.0 ) 
        PD ['low']    = EdgeCost ( 5.0 ) 
 
        resultList = []
        for e in PD: 
            resultList.append (e)
        self.failUnless ( resultList == ['low', 'medium', 'high' ] )

        self.failUnless ( len ( PD ) ==0 )

if __name__ == "__main__":

    import unittest
#    suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in module_strings]
 
    suites = unittest.defaultTestLoader.loadTestsFromName ("tests")
    testSuite = unittest.TestSuite(suites)
    text_runner = unittest.TextTestRunner().run(testSuite)


