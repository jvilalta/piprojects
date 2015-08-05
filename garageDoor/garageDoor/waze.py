import logging
import json
import urllib2

class waze():
    """description of class"""
    def get_eta(self,token):
        driveUrl="http://mobile-web.waze.com/rtserver/web/PickUpGetDriverInfo?clientID=70a8b694c7&routeTimestamp=0&getUserInfo=true&token=" + token
        logging.debug(driveUrl)
        driverInfo=json.loads(urllib2.urlopen(driveUrl).read())
        logging.debug(driverInfo)
        if driverInfo['status']=='ok':
            return int(driverInfo['eta'])
        else:
            return None

