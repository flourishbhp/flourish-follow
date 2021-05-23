import datetime
import pandas as pd
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls.base import reverse
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import (
    ListboardFilterViewMixin, SearchFormViewMixin)
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..model_wrappers import FollowAppointmentModelWrapper
from ..models import FollowExportFile
from .download_report_mixin import DownloadReportMixin
from .filters import ListboardViewFilters


class AppointmentListboardView(NavbarViewMixin, EdcBaseViewMixin,
                    ListboardFilterViewMixin, SearchFormViewMixin,
                    DownloadReportMixin, ListboardView):

    listboard_template = 'flourish_follow_appt_listboard_template'
    listboard_url = 'flourish_follow_appt_listboard_url'
    listboard_panel_style = 'info'
    listboard_fa_icon = "fa-user-plus"

    model = 'edc_appointment.appointment'
    listboard_view_filters = ListboardViewFilters()
    model_wrapper_cls = FollowAppointmentModelWrapper
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'appointments'
    ordering = '-modified'
    paginate_by = 10
    search_form_url = 'flourish_follow_appt_listboard_url'

    def get_success_url(self):
        return reverse('flourish_follow:flourish_follow_appt_listboard_url')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('subject_identifier'):
            options.update(
                {'subject_identifier': kwargs.get('subject_identifier')})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q

    def export(self, queryset=None):
        """Export data.
        """
        data = []
        for obj in queryset:
            data.append(
                {'subject_identifier': getattr(obj, 'subject_identifier'),
                 'first_name': getattr(obj, 'first_name'),
                 'last_name': getattr(obj, 'last_name'),
                 'gender': getattr(obj, 'gender'),
                 'earliesr_date_due': getattr(obj, 'earliesr_date_due'),
                 'latest_date_due': getattr(obj, 'latest_date_due'),
                 'ideal_date_due': getattr(obj, 'ideal_date_due'),
                 'appt_datetime': getattr(obj, 'appt_datetime')})
        df = pd.DataFrame(data)
        print('Here ************')
        self.download_data(
            description='Appointment and windows',
            start_date=datetime.datetime.now().date(),
            end_date=datetime.datetime.now().date(),
            report_type='appointments_window_periods', 
            df=df)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('export') == 'yes':
            queryset = context.get('object_list')  # from ListView
            self.export(queryset=queryset)
            msg = (
                f'File generated succesfully. '
                'Go to the download list to download file.')
            messages.add_message(
                self.request, messages.SUCCESS, msg)
        appointment_downloads = FollowExportFile.objects.filter(
            description='Appointment and windows').order_by('uploaded_at')
        context.update(
        appointment_downloads=appointment_downloads)
        return context
