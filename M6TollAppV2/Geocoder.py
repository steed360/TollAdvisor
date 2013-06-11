'''

Module to provide a simple Gecoder service
Public access should be via the Geocode function. 
This should return a dictionary with 

'''

import urllib2
from xml.sax import make_parser, handler, saxutils
import io
from apperror import AppError


class FirstMatchParser (handler.ContentHandler):

    '''

    SAX Parser to read the XML returned by: 

    http://nominatim.openstreetmap.org/search?q=%s&format=xml

    The XML represents a list of places found (with co-ordinates)

    The parser returns the name, lon and lat of the first match.
 
    Expects to be constructed with a reference to resultDict.
    The dictionary will be populated with data during parsing.

    @resultDict  = { place_name: None, lon: None, lat: None }
 
    '''

    def __init__(self, resultDict=None ):

        handler.ContentHandler.__init__(self)

        self.resultDict  = resultDict
        if len (resultDict)== 0:
            resultDict ['lon']          = None
            resultDict ['lat']          = None
            resultDict ['display_name'] = None

    def startElement(self, name, attrs):

        '''
        Currently only one result is required, 
        but this is easily extended to a list of 
        results that users can select from
  
        Update the object reference to resultDict

        '''

        if name == 'place' and self.resultDict['lon']==None :

            for (name, value) in attrs.items():
                if name        == 'lon':
                    self.resultDict['lon']          = saxutils.escape(value)
                elif name   == 'lat':
                    self.resultDict['lat']          = saxutils.escape(value)
                elif name   == 'display_name':
                    self.resultDict['display_name'] = saxutils.escape(value)



def geocode (txtLocation):

    '''

    Pass txtLocation to the Nominatum geocoder API.

    All being well, return a dict object with structure

    {place_name = a, longitude=b, latitude = c }

    '''

    resultDict = None
    try:

        txtLocationFmt = txtLocation.replace ( ' ', '%20' )

        URL         = "http://nominatim.openstreetmap.org/"+\
                      "search?q=%s&format=xml" %(txtLocationFmt)

        try:
            response = urllib2.urlopen (URL)

        except Exception as e:

            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'Geocoder.geocode', \
                            'Connecting to nomatum site for search: %s' %(txtLocation), e )

        parser = make_parser()
        encoding = response.headers.getparam('charset')

        resultDict = {'lon':None, 'lat':None, 'display_name': None}

        XMLText = response.read().decode(encoding)

        response.close()

        try:

            parser.setContentHandler(FirstMatchParser (resultDict) )

        except Exception as e:
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'Geocoder.geocode', \
                            'Seting content handler for search: %s' %(txtLocation), e )

        abytes = io.BytesIO(XMLText.encode('utf8'))

        try:

            parser.parse ( abytes )

        except Exception as e:
            print "here %s" %(e)
            import traceback, utils
            utils.logError ( traceback.format_exc() )
            raise AppError (utils.timestampStr (), 'Geocoder.geocode', \
                        'Doing parse for search string : %s' %(txtLocation), e )

    except Exception as e:
        import traceback, utils
        utils.logError ( traceback.format_exc() )
        raise AppError (utils.timestampStr (), 'Geocoder.geocode', \
                        'General error for search : %s' %(txtLocation), e )


    return resultDict



