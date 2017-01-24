# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-19 01:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_form_submission_orgs_to_application(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    FormSubmission = apps.get_model('intake', 'FormSubmission')
    Application = apps.get_model('intake', 'Application')
    sub = FormSubmission.objects.using(db_alias).last()
    if sub:
        sub_orgs = sub.organizations.through.objects.all()
        applications = []
        for sub_org in sub_orgs:
            app = Application(
                form_submission=sub_org.formsubmission,
                organization=sub_org.organization)
            applications.append(app)
        Application.objects.bulk_create(applications)


def empty_application_table(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Application = apps.get_model('intake', 'Application')
    Application.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_accounts', '0018_org_accepting_apps_checking_notifications'),
        ('intake', '0038_create_next_step_and_status_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='application',
            name='form_submission',
            field=models.ForeignKey(db_column='formsubmission_id', on_delete=django.db.models.deletion.PROTECT, to='intake.FormSubmission'),
        ),
        migrations.AddField(
            model_name='application',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user_accounts.Organization'),
        ),
        migrations.RunPython(copy_form_submission_orgs_to_application, empty_application_table),
        migrations.RemoveField(
            model_name='formsubmission',
            name='organizations'
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='organizations',
            field=models.ManyToManyField(related_name='submissions', through='intake.Application', to='user_accounts.Organization'),
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('additional_information', models.TextField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='intake.Application')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('next_steps', models.ManyToManyField(to='intake.NextStep')),
                ('status_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='intake.StatusType')),
            ],
        ),
    ]
