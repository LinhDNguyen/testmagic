__author__ = 'linh'
import sys
import os
import pickle
import traceback
import shutil
import time
import xmlrpclib
import zipfile

from twisted.web import xmlrpc
from twisted.web import server
from twisted.python import log

from libs.Utility import Utility


class MasterConsole(xmlrpc.XMLRPC):
    """
    Console used to control master PC
    """
    def __init__(self, host='localhost', port=1000, info={}):
        self.allowNone = True
        self.useDateTime = True
        self.allowedMethods = True
        self._port = port
        self._host = host
        self._info = info
        self._tpm = None

    def xmlrpc_ping(self, **kargs):
        """
        Get list of available test plans
        """
        pass

    def xmlrpc_run_test_case(self, info={}):
        print info
        print self._info
        return (True,)

    def xmlrpc_hello(self):
        print("HELLO FROM MASTER CONSOLE!!!")
        from testmagic.models import Family
        families = Family.objects.using('test').all()
        print(families)
        return True

    def xmlrpc_test_db(self):
        '''Use test plan manager to get all test plan.'''
        from libs.TestPlanManager import TestPlanManager
        if self._tpm is None:
            self._tpm = TestPlanManager()
            self._tpm.scan(self._info['srv_db_path'])
        print('*' * 80)
        print(self._tpm._plan_list)
        print('*' * 80)
        return True

    def xmlrpc_list_plan(self):
        '''Use test plan manager to get all test plan.'''
        from libs.TestPlanManager import TestPlanManager
        if self._tpm is None:
            self._tpm = TestPlanManager()
            self._tpm.scan(self._info['srv_db_path'])
        result = {}
        for tplan in self._tpm._plan_list:
            arr = [tplan.tp_name, tplan.tp_codename, tplan.tp_status, tplan.tp_desc, tplan.tp_specific_config]
            result[tplan.tp_codename] = arr
        return result
 
