import os
import shutil
from testmagic.models import *
from django.conf import settings


class TestPlanManager(object):
    '''This class will manage the test plans'''
    def __init__(self, origDbPath='', databaseFolder=''):
        self._plan_list = []
        self._origDb = origDbPath
        self._dbPath = databaseFolder
   
    def scan(self):
        '''This function will scan the path to detect all database and testplans in these databases.
        Each database will be added into database connection dictionary.'''
        # Clean test plan list
        self._plan_list = []
        # Clean database settings
        for k in settings.DATABASES.keys():
            if k == 'default':
                continue
            del(settings.DATABASES[k])
        # Check the path folder
        if not os.path.exists(self._dbPath):
            raise Exception("Database folder %s does not exists." % self._dbPath)
        # Walk in the path folder
        dbfiles = []
        for root, dirs, files in os.walk(self._dbPath):
            for file in files:
                if file.endswith('.sqlite3'):
                    dbfiles.append(os.path.join(root, file))
        # if slite3 file, add into db connection array
        for dbfile in dbfiles:
            dbname = os.path.basename(dbfile)
            dbname = dbname.replace('.sqlite3', '')
            if dbname in settings.DATABASES.keys():
                raise Exception("Database file %s has duplicated name." % dbfile)
            settings.DATABASES[dbname] = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': dbfile,
            }
            # Add object into array
            plans = TestPlan.objects.using(dbname).all()
            if not plans:
                continue
            for plan in plans:
                plan._connection_name = dbname
                self._plan_list.append(plan)

    def createPlan(self, planCode, planName, sameDbWith='', description='', mailList='', specificConfig=''):
        '''This function will create new test plan then add it into the list'''
        # Check test plan code exists
        if self.getTestPlan(planCode) is not None:
            raise Exception("Test plan with code %s already existed." % planCode)
        # Create test plan object
        nplan = TestPlan(tp_name=planName, tp_codename=planCode, tp_status=0, tp_desc=description,
                         tp_mail_list=mailList, tp_specific_config=specificConfig)
        # Check if test plan place at the same database with other test plan.
        if (sameDbWith) and (self.getTestPlan(sameDbWith) is not None):
            nplan.save(using=sameDbWith)
            nplan._connection_name = sameDbWith
            self._plan_list.append(nplan)
            return
        # Create database file
        if not os.path.exists(self._origDb):
            raise Exception("Original database file %s does not exists." % self._origDb)
        nplanPath = os.path.join(self._dbPath, "%s.sqlite3" % planCode)
        shutil.copyfile(self._origDb, nplanPath)
        # Add database connection into settings
        settings.DATABASES[planCode] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': nplanPath,
        }
        
        # Save the new test plan
        nplan.save(using=planCode)
        nplan._connection_name = planCode
        self._plan_list.append(nplan)

    def setActive(self, planCode, isActive):
        '''This function will set the test plan active or in-active'''
        # get the test plan
        tplan = self.getTestPlan(planCode)
        # set it active
        if isActive:
            tplan.tp_status = 1
        else:
            tplan.tp_status = 0
        tplan.save(using=tplan._connection_name)
        # Start test plan scheduler
        # @TODO start test plan scheduler

    def getTestPlan(self, plan_code):
        '''This function will get test plan from the list'''
        # browse each test plan in the list
        for plan in self._plan_list:
            if plan.tp_codename == plan_code:
                return plan
        return None
