import pandas as pd
import pytz
from datetime import datetime
from django.views.generic.base import ContextMixin
from edc_base.utils import get_utcnow

from django.http.response import HttpResponse

tz = pytz.timezone('Africa/Gaborone')


class ExportViewMixin(ContextMixin):

    requisition_model = None

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        export = self.request.GET.get('export', '')
        if export:
            response = self.export_csv()
        return response

    def export_csv(self, data=[]):
        export_data = data or [self.format_data(obj) for obj in self.object_list]

        df = pd.DataFrame(export_data)

        filename = f'{self.filename}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    def format_data(self, obj):
        data = {}
        wrapped_obj = self.model_wrapper_cls(obj)

        for field in self.export_fields:
            field_value = self.get_field_value(field, wrapped_obj)
            if field_value == '':
                field_value = self.get_field_value(
                    field, wrapped_obj.object)

            data.update({f'{field}': field_value})

        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.strftime('%d-%m-%Y %H:%M')
            if key in ['child_age', 'child_bmi']:
                data[key] = round(obj.child_age, 2)
        return data

    def get_field_value(self, field, obj):
        try:
            return getattr(obj, field, '')
        except AttributeError:
            return None

    @property
    def exclude_fields(self):
        return ['site_id', '_state', 'created', 'modified', 'revision', 'id',
                'hostname_created', 'hostname_modified', 'device_created',
                'device_modified', 'slug']

    @property
    def export_fields(self):
        return []

    @property
    def filename(self):
        cohort_name = 'cohort_c_sec'
        if self.querystring:
            cohort_name = self.querystring.split('=', 1)[1]
        file_name = f'{cohort_name}_schedule_{get_utcnow().date().strftime("%Y_%m_%d")}'

        download_path = f'{file_name}'
        return download_path
