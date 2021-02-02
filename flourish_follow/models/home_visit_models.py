from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_fields import OtherCharField
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.constants import NOT_APPLICABLE
from multiselectfield import MultiSelectField

from ..choices import UNSUCCESSFUL_VISIT, LOCATION_FOR_CONTACT, LOCATION_SUCCESS


from .worklist import WorkList


class InPersonLog(BaseUuidModel):
    """A system model to track an RA\'s attempts to confirm a Plot
    (related).
    """

    worklist = models.OneToOneField(
        WorkList,
        on_delete=PROTECT,)

    study_maternal_identifier = models.CharField(
        verbose_name='Study maternal Subject Identifier',
        max_length=50,
        unique=True)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=get_utcnow)

    history = HistoricalRecords()

    def __str__(self):
        return self.study_maternal_identifier

    class Meta:
        app_label = 'flourish_follow'


class InPersonContactAttempt(BaseUuidModel):

    in_person_log = models.ForeignKey(
        InPersonLog,
        on_delete=PROTECT,)

    study_maternal_identifier = models.CharField(
        verbose_name='Study maternal Subject Identifier',
        max_length=50,
        unique=True)

    prev_study = models.CharField(
        verbose_name='Previous Study Name',
        max_length=100, )

    contact_date = models.DateField(
        verbose_name='Date of contact attempt',
        validators=[datetime_not_future, ])

    contact_location = MultiSelectField(
        verbose_name='Which location was used for contact?',
        max_length=100,
        choices=LOCATION_FOR_CONTACT)

    successful_location = MultiSelectField(
        verbose_name='Which location(s) were successful?',
        max_length=100,
        choices=LOCATION_SUCCESS)

    phy_addr_unsuc = models.CharField(
        verbose_name='Why was the in-person visit to [Physical Address with '
                     'detailed description] unsuccessful',
        max_length=100,
        choices=UNSUCCESSFUL_VISIT,
        default=NOT_APPLICABLE)

    phy_addr_unsuc_other = OtherCharField(
        max_length=50,
        verbose_name='Visit unsuccessful other')

    workplace_unsuc = models.CharField(
        verbose_name='Why was the in-person visit to [Name and location of '
                     'workplace] unsuccessful',
        max_length=100,
        choices=UNSUCCESSFUL_VISIT,
        default=NOT_APPLICABLE)

    workplace_unsuc_other = OtherCharField(
        max_length=50,
        verbose_name='Unsuccessful visit reason other')

    contact_person_unsuc = models.CharField(
        verbose_name='Why was the in-person visit to Contact person [Full '
                     'physical address] unsuccessful',
        max_length=100,
        choices=UNSUCCESSFUL_VISIT,
        default=NOT_APPLICABLE)

    contact_person_unsuc_other = OtherCharField(
        max_length=50,
        verbose_name='Visit to Contact person unsuccessful other')

    class Meta:
        app_label = 'flourish_follow'
        verbose_name = 'In Person Contact Attempt'
        verbose_name_plural = 'In Person Contact Attempt'
