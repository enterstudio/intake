import itertools
from django.utils.translation import ugettext_lazy as _
import Levenshtein

import intake
from intake import models
from intake.constants import SMS, EMAIL
from intake.service_objects import ConfirmationNotification


class MissingAnswersError(Exception):
    pass


def check_for_existing_duplicates(submission, applicant_id):
    dups = []
    other_subs = models.FormSubmission.objects.filter(
        applicant_id=applicant_id).exclude(id=submission.id)
    for other in other_subs:
        if are_duplicates(submission, other):
            dups.append(other)
    return dups


def link_with_any_duplicates(submission, applicant_id):
    """Links submission with any duplicates from the same applicant

    If duplicates are found, returns the DuplicateSubmissionSet id
    If no duplicates are found, returns False
    """
    duplicates = check_for_existing_duplicates(submission, applicant_id)
    if duplicates:
        dup_set_id = None
        unadded_duplicates = []
        for dup in duplicates:
            if dup.duplicate_set_id:
                dup_set_id = dup.duplicate_set_id
            else:
                unadded_duplicates.append(dup)
        if not dup_set_id:
            new_dup_set = models.DuplicateSubmissionSet()
            new_dup_set.save()
            new_dup_set.submissions.add(*unadded_duplicates)
            dup_set_id = new_dup_set.id
        submission.duplicate_set_id = dup_set_id
        submission.save()
        return dup_set_id
    return False


def create_submission(form, organizations, applicant_id):
    """Save the submission data
    """
    submission = models.FormSubmission(
        answers=form.cleaned_data,
        applicant_id=applicant_id)
    submission.save()
    submission.organizations.add(*organizations)
    link_with_any_duplicates(submission, applicant_id)
    models.ApplicationEvent.log_app_submitted(applicant_id)
    return submission


def fill_pdfs_for_submission(submission):
    """Checks for and creates any needed `FilledPDF` objects
    """
    fillables = models.FillablePDF.objects.filter(
        organization__submissions=submission)
    for fillable in fillables:
        fillable.fill_for_submission(submission)


def get_permitted_submissions(user, ids=None, related_objects=False):
    query = models.FormSubmission.objects
    if related_objects:
        query = query.prefetch_related(
            'logs__user__profile__organization')
    if ids:
        query = query.filter(pk__in=ids)
    if user.is_staff:
        return query.all()
    org = user.profile.organization
    return query.filter(organizations=org)


def find_duplicates(search_space):
    duplicate_sets = []
    for pair in itertools.combinations(search_space, 2):
        if are_duplicates(*pair):
            pair_set = set(pair)
            attached_to_existing_set = False
            for dup_set in duplicate_sets:
                if dup_set & pair_set:
                    dup_set |= pair_set
                    attached_to_existing_set = True
                    break
            if not attached_to_existing_set:
                duplicate_sets.append(pair_set)
    return duplicate_sets


NAME_DIFFERENCE_THRESHOLD = 0.8


def are_duplicates(a, b):
    """Two submissions are defined as duplicates if:
        they have very similar names
        AND
        they are going to the same set of organizations
    """
    name_score = get_name_similarity_ratio(a, b)
    same_orgs = have_same_orgs(a, b)
    return name_score > NAME_DIFFERENCE_THRESHOLD and same_orgs


def get_full_lowercase_name(sub):
    return ' '.join([
        sub.answers.get(key, '')
        for key in ('first_name', 'middle_name', 'last_name')]
    ).lower()


def get_name_similarity_ratio(a, b):
    names = (get_full_lowercase_name(sub) for sub in (a, b))
    return Levenshtein.ratio(*names)


def have_same_orgs(a, b):
    a_orgs, b_orgs = (
        set(sub.organizations.values_list('id', flat=True))
        for sub in (a, b))
    return a_orgs == b_orgs


def get_confirmation_flash_messages(confirmation_notification):
    messages = []
    message_templates = {
        EMAIL: _("We've sent you an email at {}"),
        SMS: _("We've sent you a text message at {}")
    }
    for method in confirmation_notification.successes:
        template = message_templates[method]
        contact_info = confirmation_notification.contact_info[method]
        messages.append(template.format(contact_info))
    return messages


def send_confirmation_notifications(sub):
    confirmation_notification = ConfirmationNotification(sub)
    confirmation_notification.send()
    return get_confirmation_flash_messages(confirmation_notification)


# These methods are used for test setup only
def create_for_organizations(organizations, **kwargs):
    submission = models.FormSubmission(**kwargs)
    submission.save()
    submission.organizations.add(*organizations)
    return submission


def create_for_counties(counties, **kwargs):
    organizations = [
        county.get_receiving_agency(kwargs['answers'])
        for county in counties
    ]
    return create_for_organizations(
        organizations=organizations, **kwargs)