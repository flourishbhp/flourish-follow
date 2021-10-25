from datetime import timedelta
from dateutil.parser import parse
import datetime
import re

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import (
    ListboardFilterViewMixin, SearchFormViewMixin)
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..model_wrappers import BookingModelWrapper
from ..forms import AppointmentRegistrationForm
from .filters import ScreeningListboardViewFilters
from ..models import Booking
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow


class BookListboardView(NavbarViewMixin, EdcBaseViewMixin,
                               ListboardFilterViewMixin, SearchFormViewMixin,
                               ListboardView, FormView):

    form_class = AppointmentRegistrationForm
    listboard_template = 'flourish_follow_book_listboard_template'
    listboard_url = 'flourish_follow_book_listboard_url'
    listboard_panel_style = 'info'
    listboard_fa_icon = "fa-user-plus"

    model = 'flourish_follow.booking'
    listboard_view_filters = ScreeningListboardViewFilters()
    model_wrapper_cls = BookingModelWrapper
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'book'
    ordering = '-modified'
    paginate_by = 10
    search_form_url = 'flourish_follow_book_listboard_url'

    def get_success_url(self):
        return reverse('flourish_follow:flourish_follow_book_listboard_url')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('subject_cell'):
            options.update(
                {'subject_cell': kwargs.get('subject_cell')})
        if kwargs.get('first_name'):
            options.update(
                {'first_name': kwargs.get('first_name')})
        if kwargs.get('last_name'):
            options.update(
                {'last_name': kwargs.get('last_name')})
        if kwargs.get('middle_name'):
            options.update(
                {'middle_name': kwargs.get('middle_name')})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q

    def get_context_data(self, **kwargs):

        # Update booking status
        if self.request.GET.get('status') == 'done':
            subject_cell = self.request.GET.get('subject_cell')
            status = self.request.GET.get('status')
            if subject_cell and status:
                try:
                    booking = Booking.objects.get(subject_cell=subject_cell)
                except Booking.DoesNotExist:
                    raise ValidationError(
                        f"The participant with cell number {subject_cell} does not exist")
                else:
                    booking.appt_status = status
                    booking.save()
        if self.request.GET.get('status') == 'cancelled':
            subject_cell = self.request.GET.get('subject_cell')
            status = self.request.GET.get('status')
            if subject_cell and status:
                try:
                    booking = Booking.objects.get(subject_cell=subject_cell)
                except Booking.DoesNotExist:
                    raise ValidationError(
                        f"The participant with cell number {subject_cell} does not exist")
                else:
                    booking.appt_status = status
                    booking.save()

        self.object_list = self.get_queryset()

        # Bookings
        if self.request.method == 'POST':
            booking_form = AppointmentRegistrationForm(self.request.POST)
            booking_date = (booking_form['booking_date'].value())
            booking_date = parse(booking_date).date()
            update_request = self.request.POST.copy()
            update_request.update({'booking_date': booking_date})
            booking_form = AppointmentRegistrationForm(update_request)
            if booking_form.is_valid():
                first_name = booking_form.data['first_name']
                middle_name = booking_form.data['middle_name']
                last_name = booking_form.data['last_name']
                subject_cell = booking_form.data['subject_cell']
                booking_date = booking_form.data['booking_date']

                options = {
                    'first_name': first_name,
                    'middle_name': middle_name,
                    'last_name': last_name,
                    'subject_cell': subject_cell,
                    'booking_date': booking_date}
                try:
                    Booking.objects.get(subject_cell=subject_cell)
                except Booking.DoesNotExist:
                    Booking.objects.create(**options)

        booked_today = Booking.objects.filter(booking_date=get_utcnow().date()).count()
        booked_today_done = Booking.objects.filter(
            booking_date=get_utcnow().date(),
            appt_status='done').count()
        booked_today_pending = Booking.objects.filter(
            booking_date=get_utcnow().date(),
            appt_status='pending').count()
        booked_today_cancelled = Booking.objects.filter(
            booking_date=get_utcnow().date(),
            appt_status='cancelled').count()

        booked_tomorrow = Booking.objects.filter(
            booking_date=get_utcnow().date() + timedelta(days=1)).count()
        booked_tomorrow_done = Booking.objects.filter(
            booking_date=get_utcnow().date() + timedelta(days=1),
            appt_status='done').count()
        booked_tomorrow_pending = Booking.objects.filter(
            booking_date=get_utcnow().date() + timedelta(days=1),
            appt_status='pending').count()
        booked_tomorrow_cancelled = Booking.objects.filter(
            booking_date=get_utcnow().date() + timedelta(days=1),
            appt_status='cancelled').count()

        date = get_utcnow().date()
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(6)
        
        booked_this_week = Booking.objects.filter(
            booking_date__range=[start_week, end_week],).count()
        booked_this_week_done = Booking.objects.filter(
            booking_date__range=[start_week, end_week],
            appt_status='done').count()
        booked_this_week_pending = Booking.objects.filter(
            booking_date__range=[start_week, end_week],
            appt_status='pending').count()
        booked_this_week_cancelled = Booking.objects.filter(
            booking_date__range=[start_week, end_week],
            appt_status='cancelled').count()
            
        done = Booking.objects.filter(
            appt_status='done').count()
        pending = Booking.objects.filter(
            appt_status='pending').count()
        cancelled = Booking.objects.filter(
            appt_status='cancelled').count()
        total_bookings = Booking.objects.all().count()

        context = super().get_context_data(**kwargs)
        context.update(
            booked_this_week=booked_this_week,
            booked_this_week_done=booked_this_week_done,
            booked_this_week_pending=booked_this_week_pending,
            booked_this_week_cancelled=booked_this_week_cancelled,
            total_bookings=total_bookings,
            done=done,
            pending=pending,
            cancelled=cancelled,
            booked_today=booked_today,
            booked_today_cancelled=booked_today_cancelled,
            booked_tomorrow=booked_tomorrow,
            booked_today_done=booked_today_done,
            booked_today_pending=booked_today_pending,
            booked_tomorrow_done=booked_tomorrow_done,
            booked_tomorrow_cancelled=booked_tomorrow_cancelled,
            booked_tomorrow_pending=booked_tomorrow_pending)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get('start_date'):
            qs = qs.filter(appt_datetime__date__gte=self.request.GET.get('start_date'),
                           appt_datetime__date__lte=self.request.GET.get('end_date'))
        return qs
