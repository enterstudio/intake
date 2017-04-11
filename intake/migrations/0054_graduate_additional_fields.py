# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 18:38
from __future__ import unicode_literals

from django.db import migrations, models
from intake.models.form_submission import (
    QUERYABLE_ANSWER_FIELDS, DOLLAR_FIELDS)

from formation.fields import MonthlyIncome, MonthlyExpenses
from formation.form_base import Form


class MoneyValidatorForm(Form):
    fields = [
        MonthlyIncome,
        MonthlyExpenses
    ]


def copy_answers_to_fields(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    FormSubmission = apps.get_model('intake', 'FormSubmission')
    subs = FormSubmission.objects.using(db_alias).all()
    keys = QUERYABLE_ANSWER_FIELDS
    money_keys = DOLLAR_FIELDS
    for sub in subs:
        for key in keys:
            existing = sub.answers.get(key, None)
            if existing:
                setattr(sub, key, existing)
        subs_with_errors = []
        try:
            money_form = MoneyValidatorForm(sub.answers, validate=True)
            for money_key in money_keys:
                existing = money_form.cleaned_data.get(money_key, None)
                if existing:
                    setattr(sub, money_key, existing)
        except ValueError as err:
            subs_with_errors.append(sub)

        address = sub.answers.get('address')
        if address:
            for component in address:
                existing = address.get(component, None)
                if existing:
                    setattr(sub, component, existing)
        sub.save()

    # Known issue: some values cannot be parsed by the MoneyValidatorForm,
    # reporting out here (issue #705)
    print("Unable to parse dollar amounts for these subs:")
    for sub in subs_with_errors:
        print("/t{} {}".format(sub.id, sub.answers))


def empty_new_answers_fields(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    FormSubmission = apps.get_model('intake', 'FormSubmission')
    subs = FormSubmission.objects.using(db_alias).all()
    keys = QUERYABLE_ANSWER_FIELDS
    money_keys = DOLLAR_FIELDS
    for sub in subs:
        for key in keys:
            setattr(sub, key, "")
        for money_key in money_keys:
            setattr(sub, money_key, None)
        sub.save()

"""
This migration covers the remaining answers fields, except for those relating
to declaration letter and full address. The purpose of setting
these values onto explicit fields is to make SQL querying easier for most
form_submission answers.
"""


class Migration(migrations.Migration):

    dependencies = [
        ('intake', '0053_applicationtransfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='formsubmission',
            name='additional_information',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='aliases',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='being_charged',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='city',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='contact_preferences',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='currently_employed',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='dependents',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='financial_screening_note',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='finished_half_probation',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='has_children',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='has_suspended_license',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='household_size',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='how_did_you_hear',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='income_source',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='is_married',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='is_student',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='is_veteran',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='monthly_expenses',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='monthly_income',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='on_probation_parole',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='on_public_benefits',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='owes_court_fees',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='owns_home',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='pfn_number',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='preferred_pronouns',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='rap_outside_sf',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='reasons_for_applying',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='reduced_probation',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='serving_sentence',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='state',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='street',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='us_citizen',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='website',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='when_probation_or_parole',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='when_where_outside_sf',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='where_probation_or_parole',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='formsubmission',
            name='zip',
            field=models.TextField(default=''),
        ),
        migrations.RunPython(copy_answers_to_fields, empty_new_answers_fields),
    ]
