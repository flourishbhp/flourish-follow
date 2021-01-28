from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    name = 'flourish_follow'
    verbose_name = 'Flourish Follow'
    admin_site_name = 'flourish_follow_admin'
    extra_assignee_choices = ()
    assignable_users_group = 'assignable users'

    def ready(self):
        from .models import cal_log_entry_on_post_save
        from .models import worklist_on_post_save


if settings.APP_NAME == 'flourish_follow':

    from datetime import datetime
    from dateutil.tz import gettz

    from edc_appointment.appointment_config import AppointmentConfig
    from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
    from edc_appointment.constants import COMPLETE_APPT
    from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfigs
    from edc_timepoint.apps import AppConfig as BaseEdcTimepointAppConfig
    from edc_timepoint.timepoint import Timepoint
    from edc_timepoint.timepoint_collection import TimepointCollection
    from edc_visit_tracking.apps import (
        AppConfig as BaseEdcVisitTrackingAppConfig)

    class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
        configurations = [
            AppointmentConfig(
                model='edc_appointment.appointment',
                related_visit_model='flourish_caregiver.maternalvisit',
                appt_type='clinic')]

    class EdcProtocolAppConfig(BaseEdcProtocolAppConfigs):
        protocol = 'BHP0135'
        protocol_name = 'Flourish Follow'
        protocol_number = '035'
        protocol_title = ''
        study_open_datetime = datetime(
            2016, 4, 1, 0, 0, 0, tzinfo=gettz('UTC'))
        study_close_datetime = datetime(
            2020, 12, 1, 0, 0, 0, tzinfo=gettz('UTC'))

    class EdcTimepointAppConfig(BaseEdcTimepointAppConfig):
        timepoints = TimepointCollection(
            timepoints=[
                Timepoint(
                    model='edc_appointment.appointment',
                    datetime_field='appt_datetime',
                    status_field='appt_status',
                    closed_status=COMPLETE_APPT),
                Timepoint(
                    model='edc_appointment.historicalappointment',
                    datetime_field='appt_datetime',
                    status_field='appt_status',
                    closed_status=COMPLETE_APPT),
            ])

    class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
        visit_models = {
            'flourish_caregiver': (
                'maternal_visit', 'flourish_caregiver.maternalvisit'),
            'flourish_child': (
                'child_visit', 'flourish_child.childvisit'), }
