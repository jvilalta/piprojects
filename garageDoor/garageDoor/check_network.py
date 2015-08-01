import urllib2
from subprocess import call

def internet_on():
    try:
        response=urllib2.urlopen('http://attlocal.net',timeout=5)
        return True
    except urllib2.URLError as err: pass
    return False

if not internet_on():
    print "network off"
    call(["ifdown","wlan0"])
    call(["ifup","wlan0"])
else:
    print "network on"
