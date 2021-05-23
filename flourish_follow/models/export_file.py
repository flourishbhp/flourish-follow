from django.db import models
from edc_base.model_mixins import BaseUuidModel

from edc_base.sites import SiteModelMixin
from edc_search.model_mixins import SearchSlugManager
from edc_search.model_mixins import SearchSlugModelMixin as Base


class ExportFileManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, export_identifier):
        return self.get(export_identifier=export_identifier)


class SearchSlugModelMixin(Base):

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        return fields

    class Meta:
        abstract = True


class FollowExportFile(SiteModelMixin, SearchSlugModelMixin, BaseUuidModel):

    export_identifier = models.CharField(
        verbose_name="Export Identifier",
        max_length=36,
        unique=True,
        editable=False)

    study = models.CharField(
        max_length=100, blank=True,
        default='flourish')

    description = models.CharField(max_length=255, blank=True)

    document = models.FileField(upload_to='documents/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    start_date = models.DateField(
        verbose_name="Report start date",
        null=True,
        blank=True)

    end_date = models.DateField(
        verbose_name="Report end date",
        null=True,
        blank=True)

    def __str__(self):
        return f'{self.export_identifier}'

    def natural_key(self):
        return self.export_identifier

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.append('export_identifier')
        return fields

    @property
    def file_url(self):
        """Return the file url.
        """
        try:
            return self.document.url
        except ValueError:
            return None