#!/usr/bin/env python
import sys
import os
import re
import xml.dom.minidom
import xmlrpclib
import httplib
import threading
import time
import traceback

from PySide import QtCore, QtGui

APP_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)
sys.path.append(ROOT_DIR)

import libs.resources

class Station(object):

    def __init__(self, uri='', name='', rpc=None):
        self._uri = uri
        self._rpc = rpc
        self._name = name
    def __str__(self):
        if self._name:
            return "%s - %s" % (self._name, self._uri)
        else:
            return self._uri

class StationSelectorGroup(QtGui.QGroupBox):
    NROW = 6
    def __init__(self, title='', stations=[], parent=None):
        super(StationSelectorGroup, self).__init__(title, parent)
        self._stations = stations
        self._ckStations = []

        self.initUI()

    def initUI(self):
        self.gridLayout = QtGui.QGridLayout()
        self.createStations()

        self.setLayout(self.gridLayout)
    def getSelectedStations(self):
        res = []
        for ck in self._ckStations:
            if ck.isChecked():
                for s in self._stations:
                    # This station is checked, find corresponding station object
                    if re.match(r'^\d+(\.\d+){3}\:\d+$', ck.text(), re.I):
                        if s._uri == ck.text():
                            res.append(s)
                    else:
                        if s._name == ck.text():
                            res.append(s)
        return res
    def updateStations(self, stations=[]):
        for ck in self._ckStations:
            self.gridLayout.removeWidget(ck)
            ck.deleteLater()
        self._ckStations = []
        self._stations = stations
        self.createStations()

    def createStations(self):
        crow = 0
        ccol = 0
        for station in self._stations:
            s = station._uri
            if station._name:
                s = station._name
            ck = QtGui.QCheckBox(s)
            self._ckStations.append(ck)

            self.gridLayout.addWidget(ck, crow, ccol)

            crow += 1
            if crow >= StationSelectorGroup.NROW:
                crow = 0
                ccol += 1

    def checkSelected(self):
        selected = self.getSelectedStations()
        print "Selected:"
        for s in selected:
            print str(s)

class ConfigWidget(QtGui.QWidget):
    def __init__(self):
        super(ConfigWidget, self).__init__()
        self.initUI()

    def initUI(self):
        mainLayout = QtGui.QGridLayout()

        # Create configure items
        self.ckIsShell = QtGui.QCheckBox("&Is shell")

        lbActiveDir = QtGui.QLabel("Active &directory")
        self.txtActiveDir = QtGui.QLineEdit()
        lbActiveDir.setBuddy(self.txtActiveDir)

        lbTimeout = QtGui.QLabel("&Time out")
        self.txtTimeout = QtGui.QLineEdit()
        self.txtTimeout.setText('100')
        self.txtTimeout.setInputMask("90000")
        self.txtTimeout.setFixedWidth(80)
        lbTimeout.setBuddy(self.txtTimeout)

        lbOutput = QtGui.QLabel("Out&put")
        self.txtOutput = QtGui.QLineEdit()
        lbOutput.setBuddy(self.txtOutput)

        lbError = QtGui.QLabel("&Error")
        self.txtError = QtGui.QLineEdit()
        lbError.setBuddy(self.txtError)


        self.btnRefreshStation = QtGui.QPushButton("Re&fresh station")
        self.btnRefreshStation.setDefault(False)

        mainLayout.addWidget(self.ckIsShell,        0, 1, 1, 1)

        mainLayout.addWidget(lbActiveDir,           1, 0, 1, 1)
        mainLayout.addWidget(self.txtActiveDir,     1, 1, 1, 1)

        mainLayout.addWidget(lbTimeout,             2, 0, 1, 1)
        mainLayout.addWidget(self.txtTimeout,       2, 1, 1, 1)

        mainLayout.addWidget(lbOutput,              3, 0, 1, 1)
        mainLayout.addWidget(self.txtOutput,        3, 1, 1, 1)

        mainLayout.addWidget(lbError,               4, 0, 1, 1)
        mainLayout.addWidget(self.txtError,         4, 1, 1, 1)

        mainLayout.addWidget(self.btnRefreshStation, 5, 0)

        self.setLayout(mainLayout)

    def getConfig(self):
        res = {}

        res['isshell'] = self.ckIsShell.isChecked()
        res['timeout'] = int(self.txtTimeout.text().strip())
        tmp = self.txtActiveDir.text().strip()
        if len(tmp):
            res['active_dir'] = tmp
        tmp = self.txtOutput.text().strip()
        if len(tmp):
            res['output'] = tmp
        tmp = self.txtError.text().strip()
        if len(tmp):
            res['error'] = tmp

        return res

class StationControlWidget(QtGui.QWidget):
    def __init__(self):
        super(StationControlWidget, self).__init__()

        self.initUI()

    def initUI(self):
        # main layout, 11 row 10 col
        mainLayout = QtGui.QGridLayout()

        self.txtLog = QtGui.QTextEdit()
        self.txtLog.setReadOnly(True)
        lbLog = QtGui.QLabel("&Log:")
        lbLog.setBuddy(self.txtLog)
        lbLog.setFixedHeight(15)
        mainLayout.addWidget(lbLog, 0, 0, 1, 10)          # First row
        mainLayout.addWidget(self.txtLog, 1, 0, 10, 10)   # 10 rows, 10 cols

        self.txtCommand = QtGui.QLineEdit()
        self.btnRun = QtGui.QPushButton("&Run")
        self.btnRun.setFixedWidth(80)
        self.btnRun.setDefault(True)
        self.btnClear = QtGui.QPushButton("Clear lo&g")
        self.btnClear.setFixedWidth(80)
        self.btnClear.setDefault(False)
        self.btnGetAsync = QtGui.QPushButton("&Async status")
        self.btnGetAsync.setFixedWidth(80)
        self.btnGetAsync.setDefault(False)
        self.btnClose = QtGui.QPushButton("Cl&ose")
        self.btnClose.setFixedWidth(80)
        self.btnClose.setDefault(False)
        lbCommand = QtGui.QLabel("&Command")
        lbCommand.setFixedHeight(15)
        lbCommand.setBuddy(self.txtCommand)
        mainLayout.addWidget(lbCommand, 11, 0, 1, 7)
        mainLayout.addWidget(self.btnClose, 11, 7)
        mainLayout.addWidget(self.btnGetAsync, 11, 8)
        mainLayout.addWidget(self.btnClear, 11, 9)
        mainLayout.addWidget(self.txtCommand, 12, 0, 1, 9)  # 1 row, 4 cols
        mainLayout.addWidget(self.btnRun, 12, 9)            # 1 row, 1 col

        self.setLayout(mainLayout)

class MainWindow(QtGui.QMainWindow):
    TITLE = "Automation station controller"
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QtGui.QIcon(':/images/appicon.png'))
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setWindowTitle(MainWindow.TITLE)
        self.createUI()
        self.showMaximized()

    def createUI(self):
        self.mainWidget = MyStationControl()
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.widgetStationControl.btnClose.released.connect(self.close)

class MyStationControl(QtGui.QWidget):
    def __init__(self):
        super(MyStationControl, self).__init__()
        self._failCount = 0
        self._threadlock = threading.Lock()


        self.configs = self.parseConfigs(os.path.join(APP_DIR, 'configs.xml'))
        self.activeStations = []

        self.createUI()

        self.refreshStations()

        self.widgetConfigs.btnRefreshStation.setDefault(False)
        self.widgetStationControl.btnClear.setDefault(False)
        self.widgetStationControl.btnRun.setDefault(True)

    def createUI(self):
        mainLayout = QtGui.QVBoxLayout()

        self.widgetStationControl = StationControlWidget()
        self.widgetStationSelect = StationSelectorGroup(title='&Station select', stations=self.activeStations)
        self.widgetConfigs = ConfigWidget()
        self.widgetStationSelect.setMaximumHeight(170)
        self.widgetConfigs.setMaximumHeight(170)

        headLayout = QtGui.QHBoxLayout()
        headLayout.addWidget(self.widgetStationSelect)
        headLayout.addWidget(self.widgetConfigs)

        mainLayout.addLayout(headLayout)
        mainLayout.addWidget(self.widgetStationControl)

        # self.setCentralWidget(mainLayout)
        self.setLayout(mainLayout)
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)

        # Connect signals to slots
        self.widgetStationControl.btnRun.released.connect(self.runHandler)
        self.widgetConfigs.btnRefreshStation.released.connect(self.refreshStations)
        self.widgetStationControl.btnClear.released.connect(self.clearLog)
        self.widgetStationControl.txtCommand.returnPressed.connect(self.runHandler)
        self.widgetStationControl.btnGetAsync.released.connect(self.getAsyncStatus)

    def test(self):
        print "TEST"

    def clearLog(self):
        self.widgetStationControl.txtLog.clear()

    def refreshStations(self):
        self.checkActiveStations()
        self.widgetStationSelect.updateStations(self.activeStations)

    def runHandler(self):
        # Get stations
        selectedStations = self.widgetStationSelect.getSelectedStations()
        cmd = []
        txt = self.widgetStationControl.txtCommand.text().strip()
        if txt.find('^') > 0:
            cmd = txt.split('^')
        else:
            idx = txt.find(' ')
            if idx > 0:
                cmd.append(txt[:idx])
                cmd.append(txt[(idx + 1):])
            else:
                cmd.append(txt)
        info = {
            'command': cmd,
        }
        info.update(self.widgetConfigs.getConfig())
        self.runCommand(selectedStations, info)

    def logError(self, content=''):
        s = "<br /><div id='OutputLog' style='color:red'>%s</div>" % content.replace('\n', "<br />")

        # Append to text edit
        self.widgetStationControl.txtLog.insertHtml(s)
        c = self.widgetStationControl.txtLog.textCursor();
        c.movePosition(QtGui.QTextCursor.End);
        self.widgetStationControl.txtLog.setTextCursor(c);

    def log(self, station=None, content='', type=0):
        s = "<br /><div id='LogTitle' style='color:blue'>=============%s=============</div>" % str(station)
        s += "<br /><div id='OutputLog'>%s</div>" % content.replace('\n', "<br />")

        # Append to text edit
        self.widgetStationControl.txtLog.insertHtml(s)
        # c = self.widgetStationControl.txtLog.textCursor();
        # c.movePosition(QtGui.QTextCursor.End);
        # self.widgetStationControl.txtLog.setTextCursor(c);

    def getAsync(self, station=None):
        # Wait for station IDLE
        rpc = station._rpc
        uri = station._uri

        try:
            if rpc.get_status() != 0:
                time.sleep(1)
            ret, out = rpc.get_async_status()
            s = ''
            if ret:
                s += "<div style='color: green'>==RET: %s</div><br />" % str(ret)
            else:
                s += "<div style='color: red'>==RET: %s</div><br />" % str(ret)
                self._failCount += 1
            s += "<div>==OUT: %s</div>" % out
            self._threadlock.acquire(True)
            self.log(station, s)
            self._threadlock.release()
        except:
            s = "Station: %s\n" % station._uri
            s += traceback.format_exc()
            self.logError(s)
            return

    def getAsyncStatus(self):
        threads = []
        self._failCount = 0
        selectedStations = self.widgetStationSelect.getSelectedStations()
        if len(selectedStations) == 0:
            return
        s = "<br />Get async status"
        # Append to text edit
        self.widgetStationControl.txtLog.insertHtml(s)
        for station in selectedStations:
            thread = threading.Thread(target=self.getAsync, args=(station,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Summary
        s = "<br /><div style='color:green'> ALL PASSED </div>"
        if self._failCount:
            s = "<br /><div style='color:red'> %d FAILED </div>" % self._failCount
        s += "<br /><br />"
        # Append to text edit
        self.widgetStationControl.txtLog.insertHtml(s)
        c = self.widgetStationControl.txtLog.textCursor();
        c.movePosition(QtGui.QTextCursor.End);
        self.widgetStationControl.txtLog.setTextCursor(c);

    def runCMD(self, station=None, info={}, timeout=100):
        # Wait for station IDLE
        rpc = station._rpc
        uri = station._uri

        try:
            if rpc.get_status() != 0:
                time.sleep(1)
            ret, out, err = rpc.run_cmd(info)
            s = ''
            if not ret:
                s += "<div style='color: green'>==RET: %d</div><br />" % ret
            else:
                s += "<div style='color: red'>==RET: %d</div><br />" % ret
                self._failCount += 1
            s += "<div>==OUT: %s</div>" % out
            if err:
                s += "<div style='color: red'>%s</div>" % str(err)
            self._threadlock.acquire(True)
            self.log(station, s)
            self._threadlock.release()
        except:
            s = "Station: %s\n" % str(station)
            s += traceback.format_exc()
            self.logError(s)
            return

    def runCommand(self, stations=[], info={}, timeout=100):
        threads = []
        self._failCount = 0
        if len(stations) == 0:
            return
        s = "<br />CMD: [%s]" % '*'.join(info['command'])
        s += "<br />CONFIG: "
        for k in info.keys():
            if k == 'command':
                continue
            v = str(info[k])
            s += "<br />   %s = %s" % (k, v)
        # Append to text edit
        self.widgetStationControl.txtLog.insertHtml(s)
        for station in stations:
            thread = threading.Thread(target=self.runCMD, args=(station, info, timeout,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # Summary
        s = "<br /><div style='color:green'> ALL PASSED </div>"
        if self._failCount:
            s = "<br /><div style='color:red'> %d FAILED </div>" % self._failCount
        s += "<br /><br />"
        # Append to text edit
        self.widgetStationControl.txtLog.insertHtml(s)
        c = self.widgetStationControl.txtLog.textCursor();
        c.movePosition(QtGui.QTextCursor.End);
        self.widgetStationControl.txtLog.setTextCursor(c);

    def checkActiveStations(self):
        if 'stations' not in self.configs.keys():
            self.activeStations = []
            return
        needCheck = []
        needCheck.extend(self.configs['stations'])

        # Check current active station
        for i in range(len(self.activeStations), 0, -1):
            s = self.activeStations[i - 1]
            if not isinstance(s, Station):
                continue
            for j in range(len(needCheck), 0, -1):
                nc = needCheck[j-1]
                if nc['uri'] == s._uri:
                    needCheck.remove(nc)
            if not self.checkPing(s._uri):
                self.logError("Station: %s not available.\n" % s._uri)
                del(self.activeStations[i - 1])
        # Check other station
        for i in needCheck:
            if not re.match(r'^\d+(\.\d+){3}\:\d+$', i['uri'], re.I | re.M):
                continue
            # Create rpc connection
            if not self.checkPing(i['uri']):
                self.logError("Station: %s not available.\n" % i['uri'])
                continue
            try:
                rpc = xmlrpclib.Server('http://%s/' % str(i['uri']))
                rpc.ping()
                uri = i['uri']
                name = ''
                if 'name' in i.keys():
                    name = i['name']
                s = Station(uri=uri, name=name, rpc=rpc)
                self.activeStations.append(s)
            except:
                pass

    def checkPing(self, uri=''):
        try:
            with MyServerProxy('http://%s/' % uri, 1) as proxy:
                proxy.ping()
            return True
        except:
            # print "\n\n%s ping failed." % uri
            # print traceback.format_exc()
            return False


    def parseConfigs(self, filePath):
        result = {}
        xdoc = xml.dom.minidom.parse( filePath )

        # root document
        root = xdoc.childNodes[0]

        # browse each configuration
        for ele in root.childNodes:
            # Ignore text node
            if ele.nodeType == xdoc.TEXT_NODE:
                continue
            nname = ele.nodeName
            if nname != 'stations':
                nvalue = ele.childNodes[0].nodeValue
                result[nname] = nvalue
            else:
                nvalue = []
                for e in ele.childNodes:
                    station = {}
                    # stations
                    if e.nodeType == xdoc.TEXT_NODE:
                        continue
                    if e.nodeName != 'station':
                        continue
                    if e.hasAttribute('name'):
                        cname = e.getAttribute('name')
                        station['name'] = cname
                    cpath = e.childNodes[0].nodeValue
                    station['uri'] = cpath
                    nvalue.append(station)
                result[nname] = nvalue
        return result

import socket

class MyServerProxy:
    def __init__(self, url, timeout=None):
        self.__url = url
        self.__timeout = timeout
        self.__prevDefaultTimeout = None

    def __enter__(self):
        try:
            if self.__timeout:
                self.__prevDefaultTimeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(self.__timeout)
            proxy = xmlrpclib.Server(self.__url, allow_none=True)
        except Exception as ex:
            raise Exception("Unable create XMLRPC-proxy for url '%s': %s" % (self.__url, ex))
        return proxy
    def __exit__(self, type, value, traceback):
        if self.__prevDefaultTimeout is None:
            socket.setdefaulttimeout(self.__prevDefaultTimeout)

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    dbsession = None
    ret = -1
    try:
        mainWin = MainWindow()
        mainWin.show()
        ret = app.exec_()
    except Exception as ex:
        QtGui.QMessageBox.critical(None, 'ERROR', "ERROR: %s" % ex, QtGui.QMessageBox.Ok)
        sys.exit(-1)
    sys.exit(ret)
