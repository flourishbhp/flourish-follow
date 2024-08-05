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
        export_data = data or [self.format_data(obj) for obj in self.get_queryset()]

        df = pd.DataFrame(export_data)

        filename = f'{self.filename}.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    def format_data(self, obj):
        data = obj.__dict__.copy()
        for field in self.exclude_fields:
            try:
                del data[field]
            except KeyError:
                continue
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.strftime('%d-%m-%Y %H:%M')
            if key == 'age':
                data[key] = round(obj.child_age, 2)
        return data

    @property
    def exclude_fields(self):
        return ['site_id', '_state', 'created', 'modified', 'revision', 'id']

    @property
    def filename(self):
        if self.querystring:
            cohort_name = self.querystring.split('=', 1)[1]
        file_name = f'{cohort_name}_schedule_{get_utcnow().date().strftime("%Y_%m_%d")}'

        download_path = f'{file_name}'
        return download_path
