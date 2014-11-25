import sys
import os

_ROOT_DIR_ = os.path.dirname(os.path.realpath(__file__))

from twisted.application import internet, service
from twisted.web import server, resource, wsgi, static
from twisted.python import threadpool
from twisted.internet import reactor
from twisted.web import xmlrpc

from libs.MasterConsole import MasterConsole
import twresource

import logging
logging.basicConfig()

PORT = 8888

class ThreadPoolService(service.Service):
    def __init__(self, pool):
        self.pool = pool

    def startService(self):
        service.Service.startService(self)
        self.pool.start()

    def stopService(self):
        service.Service.stopService(self)
        self.pool.stop()

# Environment setup for your Django project files:
sys.path.append("magicserver")
os.environ['DJANGO_SETTINGS_MODULE'] = 'magicserver.settings'
from django.core.handlers.wsgi import WSGIHandler

# Twisted Application Framework setup:
application = service.Application('twisted-django')


# WSGI container for Django, combine it with twisted.web.Resource:
# XXX this is the only 'ugly' part: see the 'getChild' method in twresource.Root
# The MultiService allows to start Django and Twisted server as a daemon.

multi = service.MultiService()
pool = threadpool.ThreadPool()
tps = ThreadPoolService(pool)
tps.setServiceParent(multi)
resource = wsgi.WSGIResource(reactor, tps.pool, WSGIHandler())
root = twresource.Root(resource)

# Servce Django media files off of /media:
mediasrc = static.File(os.path.join(os.path.abspath("."), "magicserver/media"))
staticsrc = static.File(os.path.join(os.path.abspath("."), "magicserver/static"))
root.putChild("media", mediasrc)
root.putChild("static", staticsrc)

mstrConInfo = {
    'srv_db_path': os.path.join(_ROOT_DIR_, 'dbs'),
    'srv_db_orig_path': os.path.join(_ROOT_DIR_, 'newdb.sqlite3'),
}

r = MasterConsole(info=mstrConInfo)
reactor.listenTCP(2000, server.Site(r))

# Serve it up:
main_site = server.Site(root)
internet.TCPServer(PORT, main_site).setServiceParent(multi)
multi.setServiceParent(application)
