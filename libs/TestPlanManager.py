import os
from testmagic.models import *
from django.conf import settings


class TestPlanManager(object):
    '''This class will manage the test plans'''
    def __init__(self):
        self._plan_list = []
   
    def scan(self, path):
        '''This function will scan the path to detect all database and testplans in these databases.
        Each database will be added into database connection dictionary.'''
        # Check the path folder
        if not os.path.exists(path):
            raise Exception("Database folder %s does not exists." % path)
        # Walk in the path folder
        dbfiles = []
        for root, dirs, files in os.walk(path):
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
                plan.tp_connection_name = dbname
                self._plan_list.append(plan)

    def createPlan(self, planCode, planName, sameDbWith=''):
        '''This function will create new test plan then add it into the list'''
        # Check test plan code exists
        # Create database file
        # Add database connection into settings
        # Create test plan object

    def setActive(self, testPlan, isActive):
        '''This function will set the test plan active or in-active'''
        # get the test plan
        # set it active

    def getTestPlan(self, plan_code):
        '''This function will get test plan from the list'''
        # browse each test plan in the list
        for plan in self._plan_list:
            if plan.tp_codename == plan_code:
                return plan
        return None
