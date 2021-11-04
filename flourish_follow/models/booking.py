from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager

from ..choices import APPT_STATUS, APPT_TYPE


class BookingManager(SearchSlugManager, models.Manager):
    pass


class Booking(SiteModelMixin, SearchSlugModelMixin, BaseUuidModel):

    study_maternal_identifier = models.CharField(
        verbose_name='Study maternal Subject Identifier',
        max_length=50)

    first_name = models.CharField(
        verbose_name='First name',
        max_length=250,
        null=True)

    last_name = models.CharField(
        verbose_name='Last name',
        max_length=250,
        null=True)

    booking_date = models.DateField(
        verbose_name="Booking date",
        null=True,
    )

    appt_status = models.CharField(
        verbose_name=('Status'),
        choices=APPT_STATUS,
        max_length=25,
        default='pending',
        db_index=True)

    appt_type = models.CharField(
        verbose_name='Type of appointment',
        max_length=10,
        choices=APPT_TYPE,
        blank=True,
        null=True)

    successful = models.BooleanField(default=False)

    objects = BookingManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def natural_key(self):
        return (self.subject_cell,)

    def get_search_slug_fields(self):
        fields = ['first_name', 'last_name']
        return fields

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'flourish_follow'
        verbose_name = 'Booking'
        unique_together = ('first_name', 'last_name')
