
import time
import datetime
import logging

logger = logging.getLogger(__name__)

def timestampStr ():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def logError (aString):
    logger.error ( '-------------------------------------------' )
    logger.error (     timestampStr()              )
    logger.error ( '-------------------------------------------' )
    logger.error ( aString )
    logger.error ( '-------------------------------------------' )     
