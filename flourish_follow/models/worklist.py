from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.model_validators.date import datetime_not_future
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager


class BaseWorkManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class WorklistManager(BaseWorkManager, SearchSlugManager):
    pass


class WorkList(SearchSlugModelMixin, BaseUuidModel):

    """A model linked to the subject consent to record corrections.
    """

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        unique=True)

    report_datetime = models.DateTimeField(
        verbose_name="Correction report date ad time",
        null=True,
        validators=[
            datetime_not_future],
    )

    prev_study = models.CharField(
        max_length=25)

    is_called = models.BooleanField(default=False)

    called_datetime = models.DateTimeField(null=True)

    visited = models.BooleanField(default=False)

    objects = WorklistManager()

    def __str__(self):
        return str(self.subject_identifier,)

    def natural_key(self):
        return (self.subject_identifier, )

    def get_search_slug_fields(self):
        fields = ['subject_identifier']
        return fields

    class Meta:
        app_label = 'flourish_follow'
        verbose_name = 'Worklist'
