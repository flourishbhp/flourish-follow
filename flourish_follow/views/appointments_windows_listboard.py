import re
import pandas as pd
from dateutil import parser
from datetime import datetime, timedelta
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models.expressions import ExpressionWrapper
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import (
    ListboardFilterViewMixin, SearchFormViewMixin, )
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin
from edc_appointment.choices import NEW_APPT

from .download_report_mixin import DownloadReportMixin
from .filters import AppointmentListboardViewFilters
from ..forms import AppointmentsWindowForm
from ..model_wrappers import FollowAppointmentModelWrapper
from ..models import FollowExportFile
from ..utils import follow_utils


class AppointmentListboardView(NavbarViewMixin, EdcBaseViewMixin,
                               ListboardFilterViewMixin, SearchFormViewMixin,
                               DownloadReportMixin, ListboardView, FormMixin):
    form_class = AppointmentsWindowForm
    listboard_template = 'flourish_follow_appt_listboard_template'
    listboard_url = 'flourish_follow_appt_listboard_url'
    listboard_panel_style = 'info'
    listboard_fa_icon = "fa-user-plus"
    model = 'edc_appointment.appointment'
    listboard_view_filters = AppointmentListboardViewFilters()
    model_wrapper_cls = FollowAppointmentModelWrapper
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'appointments'
    ordering = '-modified'
    paginate_by = 10
    search_form_url = 'flourish_follow_appt_listboard_url'
    filter = None

    def __init__(self, *args, **kwarg):
        super().__init__(*args, **kwarg)
        self.start_date = None
        self.end_date = None

    def get_success_url(self):
        return reverse('flourish_follow:flourish_follow_appt_listboard_url')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('subject_identifier', None):
            options.update(
                {'subject_identifier': kwargs.get('subject_identifier')})

        if options.get('timepoint_datetime__range', None):
            options.update(
                appt_status=NEW_APPT
            )
            self.ordering = 'appt_datetime'

        return options

    def get(self, request, *args, **kwargs):
        # self.start_date = request.session.get('start_date', None)
        # self.end_date = request.session.get('end_date', None)
        # self.ordering = request.session.get('sort_by', None)

        order = request.GET.get('order_by', None)
        temp = request.session.get('order_by', None)

        self.filter = request.GET.get('f', '')

        if order and order == temp:
            self.request.session['order_by'] = f'-{order}'
        elif order:
            self.request.session['order_by'] = order

        return super(AppointmentListboardView, self).get(request, *args, **kwargs)

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(subject_identifier=search_term)
        return q

    def export(self, appointment_wrappers=[], start_date=None, end_date=None):
        """Export data.
        """
        data = []

        for obj in appointment_wrappers:
            # removed names, because it defies the protocol
            earliest_date_due = getattr(obj, 'earliest_date_due')
            latest_date_due = getattr(obj, 'latest_date_due')
            ideal_date_due = getattr(obj, 'ideal_date_due')
            appt_datetime = getattr(obj, 'appt_datetime')
            if isinstance(earliest_date_due, datetime):
                earliest_date_due = earliest_date_due.date()
            if isinstance(latest_date_due, datetime):
                latest_date_due = latest_date_due.date()
            if isinstance(ideal_date_due, datetime):
                ideal_date_due = ideal_date_due.date()
            data.append(
                {'subject_identifier': getattr(obj, 'subject_identifier'),
                 'earliest_date_due': earliest_date_due,
                 'latest_date_due': latest_date_due,
                 'ideal_date_due': ideal_date_due,
                 'appt_datetime': parser.parse(appt_datetime).date(),
                 'days_count_down': getattr(obj, 'days_count_down'),
                 'appt_status': getattr(obj, 'appt_status'),
                 'visit_code': getattr(obj, 'visit_code'),
                 'study_status': getattr(obj, 'study_status', '')})
        df = pd.DataFrame(data)
        self.download_data(
            description='Appointment and windows',
            start_date=start_date,
            end_date=end_date,
            report_type='appointments_window_periods',
            df=df,
            export_type='xlsx')

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        appointment_form = AppointmentsWindowForm()

        if self.request.GET.get('export') == 'yes':
            queryset = self.get_queryset()  # from ListView
            self.export(appointment_wrappers=list(
                FollowAppointmentModelWrapper(model_obj=obj) for obj in self.get_queryset()))
            msg = (
                f'File generated successfully.  Go to the download list to download file.')
            messages.add_message(
                self.request, messages.SUCCESS, msg)
        appointment_downloads = FollowExportFile.objects.filter(
            description='Appointment and windows').order_by('uploaded_at')
        context.update(
            filter=self.filter,
            appointment_form=appointment_form,
            appointment_downloads=appointment_downloads)
        return context

    def post(self, request, *args, **kwargs):

        start_date_post = request.POST.get('start_date', None)

        end_date_post = request.POST.get('end_date', None)

        if start_date_post and start_date_post != request.session.get('start_date', None):
            request.session['start_date'] = start_date_post
            self.start_date = request.session['start_date']
            request.session['end_date'] = None

        elif end_date_post and end_date_post != request.session.get('end_date', None):
            request.session['end_date'] = end_date_post
            self.end_date = request.session['end_date']
            request.session['start_date'] = None

        elif start_date_post and end_date_post:
            request.session['start_date'] = start_date_post
            request.session['end_date'] = start_date_post

            self.start_date = request.session['start_date']
            self.end_date = request.session['end_date']

        return super().get(request, *args, **kwargs)

    def modified_get_queryset(self):
        """Return the list of items for this view.

        Completely overrides ListView.get_queryset.

        The return value gets set to self.object_list in get()
        just before rendering to response.
        """
        filter_options = self.get_queryset_filter_options(
            self.request, *self.args, **self.kwargs)
        exclude_options = self.get_queryset_exclude_options(
            self.request, *self.args, **self.kwargs)
        if self.search_term and '|' not in self.search_term:
            search_terms = self.search_term.split('+')
            q = None
            q_objects = []
            for search_term in search_terms:
                """
                Specify fields of interest
                """
                q_objects.append(
                    Q(subject_identifier__icontains=search_term) |
                    Q(appt_status__icontains=search_term.lower().replace(' ', '_')) |
                    Q(schedule_name__icontains=search_term) |
                    Q(visit_code__icontains=search_term))

                q_objects.append(self.extra_search_options(search_term))
            for q_object in q_objects:
                if q:
                    q = q | q_object
                else:
                    q = q_object
            queryset = self.model_cls.objects.filter(
                q or Q(), **filter_options).exclude(**exclude_options)
        else:
            queryset = self.model_cls.objects.filter(
                **filter_options).exclude(
                **exclude_options)
        return queryset

    def get_queryset(self):

        qs = self.modified_get_queryset().annotate(
            ideal_due_date=F('timepoint_datetime'),
            latest_due_date=ExpressionWrapper(
                F('timepoint_datetime') + timedelta(days=44), output_field=models.DateTimeField()
            ),
        )

        sort_column = self.request.session.get('order_by', None)

        if sort_column:
            qs = qs.order_by(sort_column)

        if self.request.GET.get('f', None) == 'before_due':
            today = datetime.today()
            day15 = today + timedelta(days=15)
            qs = qs.filter(latest_due_date__range=[
                           today.isoformat(), day15.isoformat()])

        elif self.request.GET.get('f', None) == 'past_due':
            today = datetime.today() - timedelta(days=1)
            qs = qs.filter(latest_due_date__lte=today)

        if self.start_date and not self.end_date:
            qs = qs.filter(appt_datetime__date__gte=self.start_date)
        elif not self.start_date and self.end_date:
            qs = qs.filter(appt_datetime__date__lte=self.end_date)
        elif self.start_date and self.end_date:
            qs = qs.filter(appt_datetime__date__range=[
                           self.start_date, self.end_date])

        # Exclude all offstudy participants from the qs
        qs = qs.exclude(subject_identifier__in=follow_utils.caregivers_offstudy())
        return qs
