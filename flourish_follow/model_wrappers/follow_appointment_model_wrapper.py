from django.conf import settings
from edc_model_wrapper import ModelWrapper
from django.apps import apps as django_apps
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class FollowAppointmentModelWrapper(ModelWrapper):
    model = 'edc_appointment.appointment'
    querystring_attrs = ['subject_identifier']
    next_url_attrs = ['study_maternal_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'flourish_follow_appt_listboard_url')

    @property
    def ideal_date_due(self):
        """Ideal date due to see a participant.
        """
        return self.object.timepoint_datetime

    @property
    def earliest_date_due(self):
        """Returns the earlist date to see a participant.
        """
        try:
            visit_definition = self.object.visits.get(self.object.visit_code)
        except:
            return "N/A"
        else:
            return self.ideal_date_due - visit_definition.rlower

    @property
    def latest_date_due(self):
        """Returns the last date to see a participant.
        """
        try:
            visit_definition = self.object.visits.get(self.object.visit_code)
        except:
            return "N/A"
        else:
            return self.ideal_date_due + visit_definition.rlower
    
    @property
    def days_count_down(self):
        if self.latest_date_due and self.ideal_date_due:
            try:
                days = (self.latest_date_due - timezone.now()).days
            except:
                return 'N/A'
            else:
                return days
        else:
            return "N/A"
