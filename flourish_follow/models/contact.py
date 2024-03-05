from django.db import models
from edc_base.model_validators.date import date_is_future
from edc_constants.choices import YES_NO

from flourish_caregiver.models.model_mixins import CaregiverContactFieldsMixin
from ..choices import YES_NO_ST_NA


class Contact(CaregiverContactFieldsMixin):

    appt_scheduled = models.CharField(
        verbose_name='Is the participant willing to schedule an appointment',
        max_length=15,
        choices=YES_NO_ST_NA)

    appt_date = models.DateField(
        verbose_name='Appointment Date',
        validators=[date_is_future, ],
        blank=True,
        null=True)

    final_contact = models.CharField(
        verbose_name=('Is this the final contact attempt and no other calls '
                      'or home visits will be made for this participant'),
        choices=YES_NO,
        max_length=3)

    class Meta:
        app_label = 'flourish_follow'
        unique_together = ('subject_identifier', 'contact_datetime')
        verbose_name = 'Contact'
