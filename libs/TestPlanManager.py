import os
import shutil
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
        from testmagic.models import TestPlan
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
        # Re-setup the django system
        import django
        django.setup()

    def createPlan(self, planCode, planName, sameDbWith='', description='', mailList='', specificConfig=''):
        '''This function will create new test plan then add it into the list'''
        from testmagic.models import TestPlan
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

    def createCase(self, planCode='', info={}):
        if not planCode:
            raise Exception("Plan code must not be empty.")
        if planCode not in settings.DATABASES.keys():
            raise Exception("Plan code %s is not configured in database settings.")
        from testmagic.models import Family, Board, Compiler, Project, Target, ProjectTarget
        # insert/update test case
        f_name = info['f_name']
        b_name = info['b_name']
        p_name = info['p_name']
        p_path = info['p_path']
        p_is_lib = int(info['p_is_lib'])
        p_is_active = int(info['p_is_active'])
        p_is_automate = int(info['p_is_automate'])
        p_timeout = int(info['p_timeout'])
        p_timedelay = int(info['p_timedelay'])
        t_name = info['t_name']
        t_type = p_is_lib
        t_full_name = info['t_full_name']
        d_name = info['d_name']
        c_codename = info['c_name']
        c_name = c_codename
        
        # Check family
        familyq = Family.objects.using(planCode).filter(f_name=f_name)
        if familyq.count() == 1:
            family = familyq.get()
        elif familyq.count() > 1:
            family = familyq.all()[0]
        else:
            family = Family(f_name=f_name)
            family.save(using=planCode)
        
        # Check board
        boardq = Board.objects.using(planCode).filter(b_name=b_name)
        if boardq.count() == 1:
            board = boardq.get()
        elif boardq.count() > 1:
            board = boardq.all()[0]
        else:
            board = Board(b_name=b_name, b_note='', b_state=1, family=family)
            board.save(using=planCode)

        # Check compiler
        compilerq = Compiler.objects.using(planCode).filter(c_codename=c_codename)
        if compilerq.count() == 1:
            compiler = compilerq.get()
        elif compilerq.count() > 1:
            compiler = compilerq.all()[0]
        else:
            compiler = Compiler(c_name=c_name, c_codename=c_codename, c_note='')
            compiler.save(using=planCode)
        
        # Check target
        targetq = Target.objects.using(planCode).filter(t_name=t_name)
        if targetq.count() == 1:
            target = targetq.get()
        elif targetq.count() > 1:
            target = targetq.all()[0]
        else:
            target = Target(t_name=t_name, t_type=t_type, t_full_name=t_full_name)
            target.save(using=planCode)

        # Check Project
        projectq = Project.objects.using(planCode).filter(p_path=p_path, p_name=p_name)
        if projectq.count() == 1:
            project = projectq.get()
        elif projectq.count() > 1:
            project = projectq.all()[0]
        else:
            project = Project(p_name=p_name, p_path=p_path, p_is_lib=p_is_lib, p_is_active=p_is_active,
                              p_is_automate=p_is_automate, p_timeout=p_timeout, p_timedelay=p_timedelay,
                              board=board, compiler=compiler)
            project.save(using=planCode)
        
        # Check project target
        ptq = ProjectTarget.objects.using(planCode).filter(project=project, target=target)
        if ptq.count() == 0:
            pt = ProjectTarget(project=project, target=target, pt_state=1)
            pt.save(using=planCode)

        return True
