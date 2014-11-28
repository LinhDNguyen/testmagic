# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('b_id', models.AutoField(serialize=False, primary_key=True)),
                ('b_name', models.TextField()),
                ('b_note', models.TextField(blank=True)),
                ('b_state', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compiler',
            fields=[
                ('c_id', models.AutoField(serialize=False, primary_key=True)),
                ('c_name', models.TextField()),
                ('c_note', models.TextField(blank=True)),
                ('c_codename', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('cp_id', models.AutoField(serialize=False, primary_key=True)),
                ('cp_name', models.TextField()),
                ('cp_uri', models.TextField()),
                ('cp_source_dir', models.TextField(blank=True)),
                ('cp_com_port', models.IntegerField(null=True, blank=True)),
                ('cp_peri_com_port', models.IntegerField(null=True, blank=True)),
                ('cp_state', models.IntegerField()),
                ('cp_is_active', models.IntegerField()),
                ('cp_doing', models.TextField(blank=True)),
                ('cp_is_server', models.IntegerField()),
                ('cp_specific_configs', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComputerCompiler',
            fields=[
                ('cc_id', models.AutoField(serialize=False, primary_key=True)),
                ('cc_compiler_path', models.TextField(blank=True)),
                ('compiler', models.ForeignKey(related_name='computer_compilers', to='testmagic.Compiler')),
                ('computer', models.ForeignKey(related_name='computer_compilers', to='testmagic.Computer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Debugger',
            fields=[
                ('d_id', models.AutoField(serialize=False, primary_key=True)),
                ('d_name', models.TextField()),
                ('d_note', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('f_id', models.AutoField(serialize=False, primary_key=True)),
                ('f_name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('l_id', models.AutoField(serialize=False, primary_key=True)),
                ('l_type', models.IntegerField(default=0)),
                ('l_content', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('p_id', models.AutoField(serialize=False, primary_key=True)),
                ('p_name', models.TextField()),
                ('p_path', models.TextField()),
                ('p_is_lib', models.IntegerField()),
                ('p_is_active', models.IntegerField()),
                ('p_is_automate', models.IntegerField()),
                ('p_timeout', models.IntegerField()),
                ('p_timedelay', models.IntegerField()),
                ('board', models.ForeignKey(related_name='projects', to='testmagic.Board')),
                ('compiler', models.ForeignKey(related_name='projects', to='testmagic.Compiler')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTarget',
            fields=[
                ('pt_id', models.AutoField(serialize=False, primary_key=True)),
                ('pt_state', models.IntegerField()),
                ('project', models.ForeignKey(related_name='project_targets', to='testmagic.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('s_id', models.AutoField(serialize=False, primary_key=True)),
                ('s_name', models.TextField()),
                ('s_start', models.TextField()),
                ('s_note', models.TextField(blank=True)),
                ('s_specific_configs', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('t_id', models.AutoField(serialize=False, primary_key=True)),
                ('t_name', models.TextField()),
                ('t_type', models.IntegerField()),
                ('t_full_name', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('tc_id', models.AutoField(serialize=False, primary_key=True)),
                ('tc_is_active', models.IntegerField()),
                ('tc_type', models.IntegerField(null=True, blank=True)),
                ('tc_specific_configs', models.TextField(blank=True)),
                ('tc_step_list', models.TextField(blank=True)),
                ('tc_note', models.TextField(blank=True)),
                ('tc_name', models.TextField(blank=True)),
                ('tc_desc', models.TextField(blank=True)),
                ('debugger', models.ForeignKey(related_name='testcases', to='testmagic.Debugger')),
                ('project_target', models.ForeignKey(related_name='testcases', to='testmagic.ProjectTarget')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestCaseInGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tcg_order', models.IntegerField()),
                ('tcg_depends', models.TextField(blank=True)),
                ('test_case', models.ForeignKey(related_name='test_case_groups', to='testmagic.TestCase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestGroup',
            fields=[
                ('tg_id', models.AutoField(serialize=False, primary_key=True)),
                ('tg_name', models.TextField()),
                ('tg_specific_configs', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestPlan',
            fields=[
                ('tp_id', models.AutoField(serialize=False, primary_key=True)),
                ('tp_name', models.TextField()),
                ('tp_codename', models.TextField()),
                ('tp_status', models.IntegerField()),
                ('tp_desc', models.TextField(blank=True)),
                ('tp_mail_list', models.TextField(blank=True)),
                ('tp_specific_config', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestPlanGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tpg_order', models.IntegerField()),
                ('tpg_depends', models.TextField(blank=True)),
                ('test_group', models.ForeignKey(related_name='plangroups', to='testmagic.TestGroup')),
                ('test_plan', models.ForeignKey(related_name='plangroups', to='testmagic.TestPlan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('tr_id', models.AutoField(serialize=False, primary_key=True)),
                ('tr_status', models.IntegerField()),
                ('tr_start', models.TextField(blank=True)),
                ('tr_end', models.TextField(blank=True)),
                ('computer_compiler', models.ForeignKey(related_name='test_results', to='testmagic.ComputerCompiler')),
                ('session', models.ForeignKey(related_name='test_results', to='testmagic.Session')),
                ('test_case', models.ForeignKey(related_name='test_results', to='testmagic.TestCase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='testcaseingroup',
            name='test_group',
            field=models.ForeignKey(related_name='test_case_groups', to='testmagic.TestGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='session',
            name='test_plan',
            field=models.ForeignKey(related_name='test_plans', to='testmagic.TestPlan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projecttarget',
            name='target',
            field=models.ForeignKey(related_name='project_targets', to='testmagic.Target'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='log',
            name='test_result',
            field=models.ForeignKey(related_name='logs', to='testmagic.TestResult'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='computer',
            name='compilers',
            field=models.ManyToManyField(to='testmagic.Compiler', through='testmagic.ComputerCompiler'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='board',
            name='family',
            field=models.ForeignKey(related_name='boards', to='testmagic.Family'),
            preserve_default=True,
        ),
    ]
