import os
import sqlite3
import logging

class database:
    """description of class"""
    def writeStatus(self,status):
        path=os.path.join(os.path.expanduser('~pi'),'garageDoor')
        fileName=os.path.join(path,'garagedoor.db')
        conn = sqlite3.connect(fileName)
        c = conn.cursor()
        # Insert a row of data
        c.execute("INSERT INTO door_status (date,status) VALUES (datetime(),?)",[status])
        conn.commit()
        conn.close()

    def writeWazeRequest(self,token,eta):
        path=os.path.join(os.path.expanduser('~pi'),'garageDoor')
        fileName=os.path.join(path,'garagedoor.db')
        conn = sqlite3.connect(fileName)
        c = conn.cursor()
        # Insert a row of data
        sql ="INSERT INTO waze (date,token,original_eta,active) VALUES (datetime(),?,datetime('now','+{0} second'),1)".format(int(eta))
        logging.debug(sql)
        c.execute(sql,[token])
        conn.commit()
        conn.close()

    def deactivateWazeRequest(self,token):
        path=os.path.join(os.path.expanduser('~pi'),'garageDoor')
        fileName=os.path.join(path,'garagedoor.db')
        conn = sqlite3.connect(fileName)
        c = conn.cursor()
        # Insert a row of data
        sql ="UPDATE waze set active=0 WHERE token=?"
        logging.debug(sql)
        c.execute(sql,[token])
        conn.commit()
        conn.close()
    
    def getActiveWazeRoutes(self):
        path=os.path.join(os.path.expanduser('~pi'),'garageDoor')
        fileName=os.path.join(path,'garagedoor.db')
        conn = sqlite3.connect(fileName)
        c = conn.cursor()
        # Insert a row of data
        sql ="SELECT token FROM waze WHERE active<>0"
        logging.debug(sql)
        c.execute(sql)
        results=c.fetchall()
        conn.commit()
        conn.close()
        return results