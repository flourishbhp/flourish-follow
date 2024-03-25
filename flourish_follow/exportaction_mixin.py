from django.apps import apps as django_apps
from django.db.models import ManyToManyField, ForeignKey, OneToOneField
from django.utils.translation import ugettext_lazy as _

from flourish_export.admin_export_helper import AdminExportHelper


class ExportActionMixin(AdminExportHelper):

    def export_as_csv(self, request, queryset):
        records = []
        for obj in queryset:
            data = obj.__dict__.copy()

            for field in self.get_model_fields:
                if isinstance(field, ManyToManyField):
                    data.update(self.m2m_data_dict(obj, field))
                    continue
                if isinstance(field, (ForeignKey, OneToOneField, )):
                    continue
            subject_identifier = data.get('subject_identifier', None)
            data.update({'cohort_name': self.cohort_name(subject_identifier)})
            data = self.remove_exclude_fields(data)
            data = self.fix_date_formats(data)
            records.append(data)
        response = self.write_to_csv(records)
        return response

    export_as_csv.short_description = _(
        'Export selected %(verbose_name_plural)s')

    actions = [export_as_csv]

    @property
    def cohort_model_cls(self):
        return django_apps.get_model('flourish_caregiver.cohort')


    def cohort_name(self, subject_identifier):
        cohort = self.cohort_model_cls.objects.filter(
            subject_identifier=subject_identifier, current_cohort=True)
        if cohort.exists():
            return cohort[0].name
        