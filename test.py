

class T (dict):
    def __init__ (self, VAL):
        self.data = VAL

    def __str__ (self):
        return self.data

    def __repr__ (self):
        return str ( self.data ) 


t1 = T (5)
t2 = T (10)
t3 = T (15)

l = []
l.append ( t2 )
l.append ( t1 )
l.append ( t3 )

l2 = sorted ( l, key=lambda x: x.data, reverse=True) 
print (l2)
l2.pop () 
print (l2)


