from django.conf import settings
from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper


from ..model_wrappers import InPersonContactAttemptModelWrapper
from ..models import Call, Log, LogEntry, InPersonContactAttempt
from .log_entry_model_wrapper import LogEntryModelWrapper


class WorkListModelWrapper(ModelWrapper):

    model = 'flourish_follow.worklist'
    querystring_attrs = ['subject_identifier', 'study_maternal_identifier']
    next_url_attrs = ['subject_identifier', 'study_maternal_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'flourish_follow_listboard_url')

    @property
    def subject_locator(self):
        SubjectLocator = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        if self.object.subject_identifier:
            try:
                locator = SubjectLocator.objects.get(
                    subject_identifier=self.object.subject_identifier)
            except SubjectLocator.DoesNotExist:
                try:
                    locator = SubjectLocator.objects.get(
                        study_maternal_identifier=self.object.study_maternal_identifier)
                except SubjectLocator.DoesNotExist:
                    return None
                else:
                    return locator
            else:
                return locator
        return None

    @property
    def call_datetime(self):
        return self.object.called_datetime

    @property
    def call(self):
        call = Call.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        return str(call.id)

    @property
    def call_log(self):
        call = Call.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        call_log = Log.objects.get(call=call)
        return str(call_log.id)

    @property
    def log_entries(self):
        call = Call.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        return LogEntry.objects.filter(
            log__call__subject_identifier=call.subject_identifier).order_by('call_datetime')[:3]

    @property
    def home_visit_log_entries(self):
        in_person_log = getattr(self.object, 'inpersonlog')
        wrapped_entries = []
        log_entries = InPersonContactAttempt.objects.filter(
            in_person_log=in_person_log)
        for log_entry in log_entries:
            wrapped_entries.append(
                InPersonContactAttemptModelWrapper(log_entry))

        return wrapped_entries

    @property
    def home_visit_log_entry(self):
        in_person_log = getattr(self.object, 'inpersonlog')
        log_entry = InPersonContactAttempt(in_person_log=in_person_log)
        return InPersonContactAttemptModelWrapper(log_entry)

    @property
    def home_visit_required(self):
        return True

    def log_entry(self):
        log = Log.objects.get(id=self.call_log)
        logentry = LogEntry(
            log=log,
            study_maternal_identifier=self.study_maternal_identifier)
        return LogEntryModelWrapper(logentry)

    @property
    def subject_consent(self):
        return django_apps.get_model(
            'flourish_caregiver.subjectconsent').objects.filter(
            subject_identifier=self.object.subject_identifier).last()

    @property
    def may_visit_home(self):
        if self.subject_locator:
            return self.subject_locator.may_visit_home
        return None

    @property
    def first_name(self):
        if self.subject_consent:
            return self.subject_consent.first_name
        return None

    @property
    def last_name(self):
        if self.subject_consent:
            return self.subject_consent.last_name
        return None

    @property
    def contacts(self):
        if self.subject_locator:
            return ', '.join([
                self.subject_locator.subject_cell or '',
                self.subject_locator.subject_cell_alt or '',
                self.subject_locator.subject_phone or '',
                self.subject_locator.subject_phone_alt or ''])
        return None

    @property
    def survey_schedule(self):
        return None
