import datetime
import uuid
import xlwt

from django.apps import apps as django_apps
from django.db.models import ManyToManyField, ForeignKey, OneToOneField
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ExportActionMixin:

    def export_as_csv(self, request, queryset):

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % (
            self.get_export_filename())

        wb = xlwt.Workbook(encoding='utf-8', style_compression=2)
        ws = wb.add_sheet('%s')

        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        font_style.num_format_str = 'YYYY/MM/DD h:mm:ss'

        field_names = [field.name for field in self.get_fields]

        for col_num in range(len(field_names)):
            ws.write(row_num, col_num, field_names[col_num], font_style)

        for obj in queryset:
            data = []
            for field in self.get_fields:
                if isinstance(field, ManyToManyField):
                    key_manager = getattr(obj, field.name)
                    field_value = ', '.join([obj.name for obj in key_manager.all()])
                    data.append(field_value)
                    continue
                if isinstance(field, (ForeignKey, OneToOneField, )):
                    field_value = getattr(obj, field.name)
                    data.append(field_value.id)
                    continue
                field_value = getattr(obj, field.name, '')
                data.append(field_value)

            row_num += 1
            for col_num in range(len(data)):
                if isinstance(data[col_num], uuid.UUID):
                    ws.write(row_num, col_num, str(data[col_num]))
                elif isinstance(data[col_num], datetime.datetime):
                    data[col_num] = timezone.make_naive(data[col_num])
                    ws.write(row_num, col_num, data[col_num],
                             xlwt.easyxf(num_format_str='YYYY/MM/DD h:mm:ss'))
                else:
                    ws.write(row_num, col_num, data[col_num])
        wb.save(response)
        return response

    export_as_csv.short_description = _(
        'Export selected %(verbose_name_plural)s')

    actions = [export_as_csv]

    def get_export_filename(self):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = "%s-%s" % (self.model.__name__, date_str)
        return filename

    def previous_bhp_study(self, study_maternal_identifier=None):
        dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
        if study_maternal_identifier:
            try:
                dataset_obj = dataset_cls.objects.get(
                    study_maternal_identifier=study_maternal_identifier)
            except dataset_cls.DoesNotExist:
                return None
            else:
                return dataset_obj.protocol

    @property
    def get_fields(self):
        return self.model._meta.get_fields()
