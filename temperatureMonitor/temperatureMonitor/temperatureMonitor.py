import subprocess
import time
import cv2
import numpy

with open('/home/pi/monitor.log','a') as f:
    while True:
        filename='/home/pi/temperatureMonitor/image'+time.strftime('%Y%m%d%H%M%S')+'.jpg'
        subprocess.check_call('fswebcam --no-banner -r 320x240 '+ filename,stdout=f,shell=True)
        img = cv2.imread(filename,0)
        ret,th1 = cv2.threshold(img,60,255,cv2.THRESH_BINARY)
        cv2.imwrite(filename,th1)
        time.sleep(5)
