from django.urls import path, re_path
from django.views.generic.base import RedirectView
from edc_dashboard import UrlConfig
from .admin_site import flourish_follow_admin
from .views import (
    AppointmentListboardView, BookingListboardView,
    BookListboardView, CohortSwitchListboardView, ListboardView, HomeView)
from .views.cohort_switch_view_mixin import cohort_fu_enrol_redirect

app_name = 'flourish_follow'

participant_identifier = '[A-Z]{1,2}142\-[0-9A-Z\-]+'
subject_identifier = '066\-[0-9\-]+'
screening_identifier = '[A-Z0-9]{8}'
subject_cell = '7[0-9]{7}'
cohort_name_pattern = 'cohort(_[A-Za-z]+)+'
enrol_cohort_pattern = '[a-z0-9]{1}'

urlpatterns = [
    path('admin/', flourish_follow_admin.urls),
    path('home', HomeView.as_view(), name='home_url'),
    path('', RedirectView.as_view(url='admin/'), name='admin_url'),
    re_path(r'^cohort_fu_redirect/'
         f'(?P<subject_identifier>{participant_identifier})/'
         f'(?P<cohort_name>{cohort_name_pattern})/(?P<enrol_cohort>{enrol_cohort_pattern})/',
         cohort_fu_enrol_redirect, name='cohort_fu_redirect')
]

flourish_follow_listboard_url_config = UrlConfig(
    url_name='flourish_follow_listboard_url',
    view_class=ListboardView,
    label='flourish_follow_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

flourish_follow_appt_listboard_url_config = UrlConfig(
    url_name='flourish_follow_appt_listboard_url',
    view_class=AppointmentListboardView,
    label='flourish_follow_appt_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

flourish_follow_booking_listboard_url_config = UrlConfig(
    url_name='flourish_follow_booking_listboard_url',
    view_class=BookingListboardView,
    label='flourish_follow_booking_listboard',
    identifier_label='subject_cell',
    identifier_pattern=subject_cell)

flourish_follow_book_listboard_url_config = UrlConfig(
    url_name='flourish_follow_book_listboard_url',
    view_class=BookListboardView,
    label='flourish_follow_book_listboard',
    identifier_label='subject_cell',
    identifier_pattern=subject_cell)

cohort_switch_listboard_url_config = UrlConfig(
    url_name='cohort_switch_listboard_url',
    view_class=CohortSwitchListboardView,
    label='cohort_switch_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=participant_identifier)

urlpatterns += flourish_follow_listboard_url_config.listboard_urls
urlpatterns += flourish_follow_appt_listboard_url_config.listboard_urls
urlpatterns += flourish_follow_booking_listboard_url_config.listboard_urls
urlpatterns += flourish_follow_book_listboard_url_config.listboard_urls
urlpatterns += cohort_switch_listboard_url_config.listboard_urls
