import RPi.GPIO as GPIO
import time
import smtplib
import os.path
import logging
import database
import doorsettings
import util
from doorsettings import config
from waze import waze

def sendEmail(oldStatus,newStatus):
    logging.debug ("sending email")
    fromAddress=config.get('mailbox','username')
    toAddress=config.get('email','to_address')
    header = 'To:' + toAddress + '\n' + 'From: ' + fromAddress + '\n' + 'Subject: raspi monitored change \n'

    msg = header + '\n Garage door status change from: '+oldStatus+' to '+newStatus+' \n\n'
    server=smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(config.get('mailbox','username'),config.get('mailbox','password'))
    server.sendmail(fromAddress,toAddress,msg)
    f=open(fileName,'w')
    f.writelines(newStatus)
    f.flush
    f.close

def openDoor():
    logging.debug ('open door')
    GPIO.setup(17, GPIO.OUT)
    time.sleep(1)
    GPIO.cleanup()

def closeDoor():
    logging.debug ('close door')
    openDoor()

def initialize_logger(log_dir):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
     
    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
 
    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(log_dir, "error.log"),"a", encoding=None, delay="true")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_and_process_messages():
    command=util.get_email_command()

    if command:
        if "open"==command[0]:
            logging.debug("Received open command. Door status is %s",status)
            if "closed"==status:
                openDoor()

        if "close"==command[0]:
            logging.debug("Received close command. Door status is %s",status)
            if "open"==status:
                closeDoor()

        if "waze"==command[0]:
            logging.debug("Received waze message")
            util.process_waze_message(command[1])

def check_waze_routes():
    logging.debug('checking waze routes')
    db=database.database()
    routes=db.getActiveWazeRoutes()
    w=waze()
    for route in routes:
        logging.debug('route: %s',route)
        token=route[0]
        eta = w.get_eta(token)
        logging.debug('eta: %s',eta)

        if eta:
            db.update_eta(token,eta)
        else:
            db.deactivateWazeRequest(token)
            continue

        if eta <120:
            openDoor()
            db.deactivateWazeRequest(token)

path=os.path.join(os.path.expanduser('~pi'),'garageDoor')
fileName=os.path.join(path,'doorstatus.txt')
initialize_logger(path)


logging.debug('calling')
doorsettings.initialize(os.path.join(path,"settings.cfg"))
doorOpenPin=27
doorClosedPin=22

logging.debug ("set up GPIOs")

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.IN)
GPIO.setup(27,GPIO.IN)


logging.debug("will write status to " + fileName)

if not os.path.exists(path):
    logging.debug ("folder not found, creating")
    os.makedirs(path)

if os.path.isfile(fileName):
    logging.debug("status file found, reading")
    f=open(fileName,'r')
    oldStatus=f.read()
    f.close
else:
    print "status file not found"
    oldStatus="unknown"

#status="unknown"
logging.debug("oldStatus%s",oldStatus)
#while True:
#print "sleeping"
#time.sleep(60)
#print "woke up"

logging.debug("pin 22 value=%s",GPIO.input(22)) # 1=closed
logging.debug("pin 27 value=%s",GPIO.input(27)) # 1=open
    
if GPIO.input(doorClosedPin)==1 :
    status="closed"
    #continue

if GPIO.input(doorOpenPin)==1 :
    status="open"
    #continue

if GPIO.input(doorOpenPin)==0 and GPIO.input(doorClosedPin)==0  :
    status= "transit"
    #continue
logging.debug ("status=%s",status)

if oldStatus!=status:
    logging.debug("oldStatus is different from status, sending email")
    sendEmail(oldStatus,status)
    oldStatus=status
    db= database.database()
    db.writeStatus(status)

check_and_process_messages()

check_waze_routes()

