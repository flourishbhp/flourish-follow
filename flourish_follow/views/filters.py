from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters
from datetime import timedelta
import datetime
from edc_base.utils import get_utcnow
from edc_appointment.choices import (
    NEW_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    COMPLETE_APPT,
    CANCELLED_APPT
)


class AppointmentListboardViewFilters(ListboardViewFilters):
    # Filters by appointments
    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    new_appt = ListboardFilter(
        label='New',
        position=1,
        lookup={'appt_status': NEW_APPT})

    in_progress_appt = ListboardFilter(
        label='In Progress',
        position=2,
        lookup={'appt_status': IN_PROGRESS_APPT})

    incomplete_appt = ListboardFilter(
        label='Incomplete',
        position=3,
        lookup={'appt_status': INCOMPLETE_APPT})

    complete_appt = ListboardFilter(
        label='Complete',
        position=4,
        lookup={'appt_status': COMPLETE_APPT})

    cancelled_appt = ListboardFilter(
        label='Cancelled',
        position=5,
        lookup={'appt_status': CANCELLED_APPT})

    # Filter by schedule names
    birth = ListboardFilter(
        label='Birth',
        position=6,
        lookup={'schedule_name__icontains': 'birth'})

    antenatal = ListboardFilter(
        label='Antenatal',
        position=7,
        lookup={'schedule_name__icontains': 'antenatal'})

    enrollment = ListboardFilter(
        label='Enrollment',
        position=8,
        lookup={'schedule_name__icontains': 'enroll'})

    quarterly = ListboardFilter(
        label='Quarterly',
        position=9,
        lookup={'schedule_name__icontains': 'quart'}
    )

    # filter by date
    before_due = ListboardFilter(
        label='15 Days Before Due',
        position=10,
        lookup={'appt_status': NEW_APPT,
                'schedule_name__icontains': 'quart'}
    )

    past_due = ListboardFilter(
        label='Past due date',
        position=10,
        lookup={'appt_status': NEW_APPT}
    )


class WorkListboardViewFilters(ListboardViewFilters):
    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    is_called = ListboardFilter(
        label='Called',
        position=10,
        lookup={'is_called': True})

    visited = ListboardFilter(
        label='Visited',
        position=11,
        lookup={'visited': True})


class ScreeningListboardViewFilters(ListboardViewFilters):
    date = get_utcnow().date()
    start_week = date - datetime.timedelta(date.weekday())
    end_week = start_week + datetime.timedelta(6)

    all = ListboardFilter(
        name='all',
        label='All',
        lookup={})

    today = ListboardFilter(
        label='Today',
        position=6,
        lookup={'booking_date': get_utcnow().date()})

    tomorrow = ListboardFilter(
        label='Tomorrow',
        position=6,
        lookup={'booking_date': get_utcnow().date() + timedelta(days=1)})

    this_week = ListboardFilter(
        label='This Week',
        position=10,
        lookup={'booking_date__range': [start_week, end_week]})

    pending = ListboardFilter(
        label='Pending',
        position=6,
        lookup={'appt_status': 'pending'})

    done = ListboardFilter(
        label='Done',
        position=6,
        lookup={'appt_status': 'done'})

    cancelled = ListboardFilter(
        label='Cancelled',
        position=6,
        lookup={'appt_status': 'cancelled'})


class CohortSwitchListboardFilters(ListboardViewFilters):

    clear = ListboardFilter(
        name='cohort_switch',
        label='Cohort Switch',
        lookup={})

    cohort_a = ListboardFilter(
        label='Cohort A',
        position=1,
        lookup={'name': 'cohort_a'})

    cohort_b = ListboardFilter(
        label='Cohort B',
        position=2,
        lookup={'name': 'cohort_b'})

    cohort_c = ListboardFilter(
        label='Cohort C',
        position=3,
        lookup={'name': 'cohort_c'})

