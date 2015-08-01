import imaplib
import email
import logging
import urllib2
from urllib2 import urlparse as urlparse
import httplib
import json
from database import database
from doorsettings import config

def check_label(label, mail):
    body=None
    rv, data = mail.select(label)
    logging.debug('select %s returned %s',label,rv)
    if rv == 'OK':
        rv, data = mail.search(None, "ALL")
        logging.debug('searching all returned %s with data %s',rv,data)
        if rv == 'OK' and data[0]!='':
            rv, data = mail.fetch(1, '(RFC822)')
            if rv == 'OK':
                msg = email.message_from_string(data[0][1])
                body = msg.get_payload(0).as_string()
                mail.store(1,'+FLAGS','\\Deleted')
                mail.expunge()
    else:
      print "No messages found!"
    return body

def check_email():
    body=None
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(config.get('mailbox','username'),config.get('mailbox','password'))
    body = check_label("commands",mail)
    if not body:
        body=check_label("waze",mail)

    mail.close()
    mail.logout()
    return body

def get_waze_id(message):
    position=message.find('waze.to/')
    logging.debug('found waze link at %s',position)
    token=message[position+8:].strip()
    logging.debug('found token %s',token)
    return token

def get_email_command():
    message = check_email()
    if not message:
        return None

    if "waze" in message:
        return ["waze",get_waze_id(message)]
    elif "close" in message.lower():
       return ["close"]
    elif "open" in message.lower():
        return ["open"]
    else:
        return None

def insert_waze_request(token,eta):
    logging.debug('insert_waze_request(%s,%s)',token,eta)
    db=database()
    db.writeWazeRequest(token,eta)

def  deactivate_waze_request(token):
    logging.debug('deactivate_waze_request(%s)',token)
    db=database()
    db.deactivateWazeRequest(token)

def process_waze_message(token):
    connection=httplib.HTTPConnection("waze.to")
    connection.request("GET","/"+token)
    response=connection.getresponse()
    meetingUrl=response.getheader("location")
    logging.debug(meetingUrl)

    querystring=urlparse.urlparse(meetingUrl).query
    token= urlparse.parse_qs(querystring)["token"][0]
    logging.debug(token)

    meetingInfoUrl="http://mobile-web.waze.com/SocialMediaServer/internal/getMeetingInfo?event_id="+ token
    logging.debug(meetingInfoUrl)
    meetingInfo=json.loads(urllib2.urlopen(meetingInfoUrl).read())
    logging.debug(meetingInfo)

    driveUrl="http://mobile-web.waze.com/rtserver/web/PickUpGetDriverInfo?clientID=70a8b694c7&routeTimestamp=0&getUserInfo=true&token=" + token
    logging.debug(driveUrl)
    driverInfo=json.loads(urllib2.urlopen(driveUrl).read())
    logging.debug(driverInfo)
    if driverInfo['status']=='ok':
        eta = driverInfo['eta']
        insert_waze_request(token,eta)
    else:
        deactivate_waze_request(token)