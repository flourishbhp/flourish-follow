from django.db import models
from edc_base.model_mixins import BaseUuidModel


class CaregiverLocator(BaseUuidModel):

    study_maternal_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    locator_date = models.DateField(max_length=25)

    may_call = models.CharField(max_length=25,
                                blank=True,
                                null=True)

    subject_cell = models.CharField(max_length=25,
                                    blank=True,
                                    null=True)

    subject_phone = models.CharField(max_length=10,
                                     blank=True,
                                     null=True)
