from django.core.exceptions import ValidationError
from django.db import models
from multiselectfield import MultiSelectField

from edc_base.model_fields import OtherCharField
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import date_is_future, datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO, NOT_APPLICABLE

from edc_call_manager.model_mixins import (
    CallModelMixin, LogModelMixin)
from flourish_caregiver.models.maternal_dataset import MaternalDataset

from ..choices import (
    APPT_GRADING, APPT_LOCATIONS,
    APPT_TYPE,
    CONTACT_FAIL_REASON, MAY_CALL, PHONE_USED, PHONE_SUCCESS,
    HOME_VISIT, YES_NO_ST_NA)
from .list_models import ReasonsUnwilling


class Call(CallModelMixin, BaseUuidModel):
    scheduled = models.DateTimeField(
        default=get_utcnow)

    class Meta(CallModelMixin.Meta):
        app_label = 'flourish_follow'


class Log(LogModelMixin, BaseUuidModel):
    call = models.ForeignKey(Call, on_delete=models.PROTECT)

    class Meta(LogModelMixin.Meta):
        app_label = 'flourish_follow'


class LogEntry(BaseUuidModel):
    log = models.ForeignKey(Log, on_delete=models.PROTECT)

    subject_identifier = models.CharField(
        max_length=50,
        blank=True, )

    screening_identifier = models.CharField(
        verbose_name="Eligibility Identifier",
        max_length=36,
        blank=True,
        null=True)

    study_maternal_identifier = models.CharField(
        verbose_name='Study maternal Subject Identifier',
        max_length=50)

    prev_study = models.CharField(
        verbose_name='Previous Study Name',
        max_length=100, )

    call_datetime = models.DateTimeField(
        default=get_utcnow,
        validators=[datetime_not_future, ],
        verbose_name='Date of contact attempt')

    phone_num_type = MultiSelectField(
        verbose_name='Which phone number(s) was used for contact?',
        choices=PHONE_USED)

    phone_num_success = MultiSelectField(
        verbose_name='Which number(s) were you successful in reaching?',
        choices=PHONE_SUCCESS)

    cell_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    alt_cell_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    tel_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    alt_tel_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    work_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    cell_alt_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    tel_alt_contact_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    cell_resp_person_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    tel_resp_person_fail = models.CharField(
        verbose_name='Why was the contact to [ ] unsuccessful?',
        max_length=100,
        choices=CONTACT_FAIL_REASON,
        default=NOT_APPLICABLE)

    appt = models.CharField(
        verbose_name='Is the participant willing to schedule an appointment',
        max_length=10,
        choices=YES_NO_ST_NA,
        default=NOT_APPLICABLE)

    appt_type = models.CharField(
        verbose_name='Type of appointment',
        max_length=10,
        choices=APPT_TYPE,
        blank=True,
        null=True)

    other_appt_type = models.CharField(
        verbose_name='Specify other type of appointment',
        max_length=10,
        null=True,
        blank=True)

    appt_reason_unwilling = models.ManyToManyField(
        ReasonsUnwilling,
        verbose_name=('What is the reason the participant is unwilling to '
                      'schedule an appointment'),
        blank=True)

    appt_reason_unwilling_other = models.CharField(
        verbose_name='Other reason, please specify ...',
        max_length=50,
        null=True,
        blank=True)

    appt_date = models.DateField(
        verbose_name="Appointment Date",
        validators=[date_is_future],
        null=True,
        blank=True,
        help_text="This can only come from the participant.")

    appt_grading = models.CharField(
        verbose_name='Is this appointment...',
        max_length=25,
        choices=APPT_GRADING,
        null=True,
        blank=True)

    appt_location = models.CharField(
        verbose_name='Appointment location',
        max_length=50,
        choices=APPT_LOCATIONS,
        null=True,
        blank=True)

    appt_location_other = OtherCharField(
        verbose_name='Other location, please specify ...',
        max_length=50,
        null=True,
        blank=True)

    delivered = models.BooleanField(
        null=True,
        default=False,
        editable=False)

    may_call = models.CharField(
        verbose_name='May we continue to contact the participant?',
        max_length=10,
        choices=MAY_CALL,
        default=YES)

    home_visit = models.CharField(
        verbose_name='Perform home visit.',
        max_length=50,
        choices=HOME_VISIT,
        default=NOT_APPLICABLE)

    home_visit_other = models.CharField(
        verbose_name='Other reason, please specify ...',
        max_length=50,
        null=True,
        blank=True)

    def save(self, *args, **kwargs):
        if not self.screening_identifier:
            try:
                maternal_dataset = MaternalDataset.objects.get(
                    study_maternal_identifier=self.study_maternal_identifier)
            except MaternalDataset.DoesNotExist:
                raise ValidationError(
                    f'Dataset object missing. for {self.study_maternal_identifier}')
            else:
                self.screening_identifier = maternal_dataset.screening_identifier
        super().save(*args, **kwargs)

    @property
    def subject(self):
        """Override to return the FK attribute to the subject.

        expects any model instance with fields ['first_name', 'last_name', 'gender', 'dob'].

        For example: self.registered_subject.

        See also: CallSubjectViewMixin.get_context_data()"""
        return None

    @property
    def outcome(self):
        outcome = []
        if self.appt_date:
            outcome.append('Appt. scheduled')
        elif self.may_call == NO:
            outcome.append('Do not call')
        return outcome

    @property
    def log_entries(self):
        # return self.objects.filter()
        return LogEntry.objects.filter(log__id=self.log.id)

    class Meta:
        unique_together = ('call_datetime', 'log')
        app_label = 'flourish_follow'
        verbose_name = 'Call Log Entry'
        verbose_name_plural = 'Call Log Entries'
