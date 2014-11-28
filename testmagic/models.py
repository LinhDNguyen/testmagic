# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Compiler(models.Model):
    ''' This class is object representation of Compiler table.
    '''
    c_id = models.AutoField(primary_key=True)
    c_name = models.TextField()
    c_note = models.TextField(blank=True)
    c_codename = models.TextField(blank=True)

    def __str__(self):
        return str(self.c_name)


class Computer(models.Model):
    cp_id = models.AutoField(primary_key=True)
    cp_name = models.TextField()
    cp_uri = models.TextField()
    cp_source_dir = models.TextField(blank=True)
    cp_com_port = models.IntegerField(blank=True, null=True)
    cp_peri_com_port = models.IntegerField(blank=True, null=True)
    cp_state = models.IntegerField()
    cp_is_active = models.IntegerField()
    cp_doing = models.TextField(blank=True)
    cp_is_server = models.IntegerField()
    cp_specific_configs = models.TextField(blank=True)
    compilers = models.ManyToManyField(Compiler, through='ComputerCompiler')

    def __str__(self):
        return str(self.cp_name)


class Debugger(models.Model):
    d_id = models.AutoField(primary_key=True)
    d_name = models.TextField()
    d_note = models.TextField(blank=True)

    def __str__(self):
        return str(self.d_name)


class Family(models.Model):
    f_id = models.AutoField(primary_key=True)
    f_name = models.TextField()

    def __str__(self):
        return str(self.f_name)


class Board(models.Model):
    b_id = models.AutoField(primary_key=True)
    b_name = models.TextField()
    b_note = models.TextField(blank=True)
    b_state = models.IntegerField()
    family = models.ForeignKey(Family, related_name='boards')

    def __str__(self):
        return str(self.b_name)


class Target(models.Model):
    t_id = models.AutoField(primary_key=True)
    t_name = models.TextField()
    t_type = models.IntegerField()
    t_full_name = models.TextField(blank=True)

    def __str__(self):
        return str(self.t_name)


class ComputerCompiler(models.Model):
    cc_id = models.AutoField(primary_key=True)
    computer = models.ForeignKey(Computer, related_name='computer_compilers')
    compiler = models.ForeignKey(Compiler, related_name='computer_compilers')
    cc_compiler_path = models.TextField(blank=True)

    def __str__(self):
        return str(self.cp_id) + '_' + str(self.cc_id)


class Project(models.Model):
    p_id = models.AutoField(primary_key=True)
    p_name = models.TextField()
    p_path = models.TextField()
    p_is_lib = models.IntegerField()
    p_is_active = models.IntegerField()
    p_is_automate = models.IntegerField()
    p_timeout = models.IntegerField()
    p_timedelay = models.IntegerField()
    board = models.ForeignKey(Board, related_name='projects')
    compiler = models.ForeignKey(Compiler, related_name='projects')

    def __str__(self):
        return str(self.p_name)


class ProjectTarget(models.Model):
    pt_id = models.AutoField(primary_key=True)
    pt_state = models.IntegerField()
    target = models.ForeignKey(Target, related_name='project_targets')
    project = models.ForeignKey(Project, related_name='project_targets')

    def __str__(self):
        return str(self.pt_id)


class TestCase(models.Model):
    tc_id = models.AutoField(primary_key=True)
    tc_is_active = models.IntegerField()
    tc_type = models.IntegerField(blank=True, null=True)
    tc_specific_configs = models.TextField(blank=True)
    tc_step_list = models.TextField(blank=True)
    tc_note = models.TextField(blank=True)
    tc_name = models.TextField(blank=True)
    tc_desc = models.TextField(blank=True)
    project_target = models.ForeignKey(ProjectTarget, related_name='testcases')
    debugger = models.ForeignKey(Debugger, related_name='testcases')

    def __str__(self):
        return str(self.tc_name)


class TestGroup(models.Model):
    tg_id = models.AutoField(primary_key=True)
    tg_name = models.TextField()
    tg_specific_configs = models.TextField(blank=True)

    def __str__(self):
        return str(self.tg_name)


class TestCaseGroup(object):
    """Group of test case"""

    def __init__(self, test_cases=[], test_group=None):
        """Constructor for TestCaseGroup"""
        self._test_cases = test_cases
        self._test_group = test_group
        self._group_id = None
        self._case_ids = []
        self._run_count = 0


class TestPlan(models.Model):
    tp_id = models.AutoField(primary_key=True)
    tp_name = models.TextField()
    tp_codename = models.TextField()
    tp_status = models.IntegerField()
    tp_desc = models.TextField(blank=True)
    tp_mail_list = models.TextField(blank=True)
    tp_specific_config = models.TextField(blank=True)
    _connection_name = ''
    _registered_slave = []
    _schedule = []
    _threads = []
    _threads_run = {}
    _lock = None

    def __str__(self):
        return str(self.tp_name)

    def loadSchedule(self):
        '''Load all test group into schedule array'''
        for plangroup in self.plangroups:
            group = TestCaseGroup()
            group._group_id = plangroup.id
            for tc in plangroup.testgroup.test_case_groups:
                group._case_ids.append(tc.tc_id)
            self._schedule.append(group)            


class Session(models.Model):
    s_id = models.AutoField(primary_key=True)
    s_name = models.TextField()
    s_start = models.TextField()  # This field type is a guess.
    s_note = models.TextField(blank=True)
    s_specific_configs = models.TextField(blank=True)
    test_plan = models.ForeignKey(TestPlan, related_name='test_plans')

    def __str__(self):
        return str(self.s_name)


class TestCaseInGroup(models.Model):
    test_case = models.ForeignKey(TestCase, related_name='test_case_groups')
    test_group = models.ForeignKey(TestGroup, related_name='test_case_groups')
    tcg_order = models.IntegerField()
    tcg_depends = models.TextField(blank=True)


class TestResult(models.Model):
    tr_id = models.AutoField(primary_key=True)
    tr_status = models.IntegerField()
    tr_start = models.TextField(blank=True)
    tr_end = models.TextField(blank=True)
    session = models.ForeignKey(Session, related_name='test_results')
    test_case = models.ForeignKey(TestCase, related_name='test_results')
    computer_compiler = models.ForeignKey(ComputerCompiler, related_name='test_results')


class TestPlanGroup(models.Model):
    test_plan = models.ForeignKey(TestPlan, related_name='plangroups')
    test_group = models.ForeignKey(TestGroup, related_name='plangroups')
    tpg_order = models.IntegerField()
    tpg_depends = models.TextField(blank=True)


class Log(models.Model):
    l_id = models.AutoField(primary_key=True)
    l_type = models.IntegerField(blank=False, default=0)
    l_content = models.TextField(blank=False)
    test_result = models.ForeignKey(TestResult, related_name='logs')

