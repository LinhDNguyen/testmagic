import os
import sys
import threading
import time

def nowexit():
    print "Exit"
    os._exit(1)

if __name__ == '__main__':
    t = threading.Timer(1, nowexit)
    t.setDaemon(True)
    t.start()
    time.sleep(5)
    print "END"
