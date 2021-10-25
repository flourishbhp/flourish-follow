from edc_dashboard.listboard_filter import ListboardFilter, ListboardViewFilters
from datetime import timedelta
import datetime

from edc_base.utils import get_utcnow


class ListboardViewFilters(ListboardViewFilters):

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
