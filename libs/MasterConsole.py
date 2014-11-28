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
        '''Ping to the server'''
        pass

    def xmlrpc_create_plan(self, info={}):
        '''Use test plan manager to create test plan.'''
        from libs.TestPlanManager import TestPlanManager
        if self._tpm is None:
            self._tpm = TestPlanManager(self._info['srv_db_orig_path'], self._info['srv_db_path'])
            self._tpm.scan()
        # Create new test plan
        try:
            self._tpm.createPlan(planCode=info['code'], planName=info['name'],
                                 sameDbWith=info['sameWith'], description=info['desc'],
                                 mailList=info['maillist'], specificConfig=info['specificConfig'])
        except Exception as ex:
            print(traceback.format_exc())
            return False
        print('*' * 80)
        self._tpm.scan()
        print(self._tpm._plan_list)
        print('*' * 80)
        return True

    def xmlrpc_list_plan(self):
        '''Use test plan manager to get all test plan.'''
        from libs.TestPlanManager import TestPlanManager
        if self._tpm is None:
            self._tpm = TestPlanManager(self._info['srv_db_orig_path'], self._info['srv_db_path'])
            self._tpm.scan()
        result = {}
        for tplan in self._tpm._plan_list:
            arr = [tplan.tp_name, tplan.tp_codename, tplan.tp_status, tplan.tp_desc, tplan.tp_specific_config]
            result[tplan.tp_codename] = arr
        return result

    def xmlrpc_new_test_case(self, planCode='', info={}):
        '''Insert/update the test case into database'''
        if not planCode:
            return False
        from libs.TestPlanManager import TestPlanManager
        if self._tpm is None:
            self._tpm = TestPlanManager(self._info['srv_db_orig_path'], self._info['srv_db_path'])
            self._tpm.scan()
        try:
            self._tpm.createCase(planCode, info)
        except Exception as ex:
            print(traceback.format_exc())
            return False
        return True
