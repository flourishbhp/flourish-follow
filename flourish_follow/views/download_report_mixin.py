import os

from django.conf import settings

from ..identifiers import ExportIdentifier
from ..models import FollowExportFile


class DownloadReportMixin:

    def download_data(
            self, description=None, start_date=None,
            end_date=None, report_type=None, df=None, export_type='csv'):
        """Export all data.
        """

        export_identifier = ExportIdentifier().identifier

        options = {
            'description': description,
            'export_identifier': export_identifier,
            'start_date': start_date,
            'end_date': end_date
        }
        doc = FollowExportFile.objects.create(**options)

        # Document path
        upload_to = FollowExportFile.document.field.upload_to
        fname = export_identifier + f'.{export_type}'
        final_path = upload_to + report_type + '/' + fname

        # Export path
        export_path = settings.MEDIA_ROOT + '/documents/' + report_type + '/'
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        export_path += fname
        if export_type == 'csv':
            df.to_csv(export_path, encoding='utf-8', index=False)
        if export_type == 'xlsx':
            df.to_excel(export_path, encoding='utf-8', index=False)

        doc.document = final_path
        doc.save()
