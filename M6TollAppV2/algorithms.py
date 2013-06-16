
from DataStructures import d_priority_dict
from DataStructures import priority_dict

'''

Routines for shortest path routing from A->B

Contains

Dijkstra2          Classic Dijkstra returning list of predecessors and 
                   list of distances to source for each node

shortestPath2      Returns a set of GISEdges representing cost, distance 
                   and geometry from A-B

'''


def Dijkstra2(G,start,end=None):

	"""
        Based on  David Eppstein, UC Irvine, 4 April 2002
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228

        JS made two changes:
        1. Allow G[v][w] to be of type EdgeCost, rather than float
        2. Conduct the routing search at both ends. 
           Based on fact that if   AreaImproved = 2 * pi * (r/2) ^ 2 
                              and  AreaOriginal = 1 * pi *  r    ^ 2
                              then AreaImproved < AreaOriginal
    
	"""

	D = {}	# dictionary of final distances (float)
	P = {}	# dictionary of predecessors (float)
        L = {}  # dictionary of links to predessor of type EdgeCost 

        midPoint = None

        end2     = start
        start2   = end

	D2 = {}	# dictionary of final distances (float)
	P2 = {}	# dictionary of predecessors (float)
        L2 = {}  # dictionary of links to predessor of type EdgeCost 
     
	Q  = priority_dict()   
	Q2 = priority_dict()   

	Q [start]  = 0
	Q2[start2] = 0

        last_v  = None
        last_v2 = None

        while Q or Q2:


            # Search out from the start
            v  = Q.smallest  ()
   
            if last_v == v: 
                # This is a workaround for rare network inconsistencies.
                Q.pop_smallest ()
                v  = Q.smallest  () 

	    D[v]   = Q[v]

	    if v == end: 
                break
            if v <> None and v in D2: 
                midPoint = v
                break

            for w in G[v]:
                vwLength = D[v] + (G[v][w]).getCost ()
                if w in D:
                    if vwLength < D[w]:
		        raise ValueError, \
                        "Dijkstra: found better path to already-final vertex"
    	        elif w not in Q or vwLength < Q[w]:
                    Q[w] = vwLength
		    P[w] = v
                    L[w] = G[v][w]

            # Search out from the end

            v2 = Q2.smallest ()

            if last_v2 == v2: 
                # This is a workaround rare network inconsistencies.
                Q2.pop_smallest ()
                v2  = Q.smallest  () 


            D2[v2] = Q2[v2]

            if v2 == end2: 
                break
            if v2 <> None and v2 in D: 
                midPoint = v2
                break

            for w2 in G[v2]:

                vwLength = D2[v2] + (G[v2][w2]).getCost ()
                if w2 in D2:
                    if vwLength < D2[w2]:
		        raise ValueError, \
                        "Dijkstra: found better path to already-final vertex"
    	        elif w2 not in Q2 or vwLength < Q2[w2]:

                    Q2[w2] = vwLength

		    P2[w2] = v2
                    L2[w2] = G[v2][w2]

            last_v  = v
            last_v2 = v2

            Q.pop_smallest ()
            Q2.pop_smallest ()

        print "returning"

        return P, P2, L, L2, midPoint


def shortestPath2(G,start,end):
	"""
	Find a single shortest path from the given start vertex
	to the given end vertex.
	The input has the same conventions as Dijkstra().
	The output is a list of the vertices in order along
	the shortest path.
	"""

	P,P2,L,L2,midPoint = Dijkstra2(G,start,end)

	Path = []

        tmpMidPoint = midPoint
	while 1:
                try:
    		    Path.append( L[tmpMidPoint] )
                except:
                    pass
		if tmpMidPoint == start: break
		tmpMidPoint = P[tmpMidPoint]

        Path2 = []

        tmpMidPoint = midPoint
	while 1:
                try:
    		    Path2.append( L2[tmpMidPoint] )
                except:
                    pass

		if tmpMidPoint == end: break
		tmpMidPoint = P2[tmpMidPoint]

	return Path + Path2



