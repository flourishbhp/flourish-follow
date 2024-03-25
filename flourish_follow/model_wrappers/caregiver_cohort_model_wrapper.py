from django.conf import settings
from edc_model_wrapper import ModelWrapper
from flourish_dashboard.model_wrappers.caregiver_locator_model_wrapper_mixin import (
    CaregiverLocatorModelWrapperMixin)

from .caregiver_contact_model_wrapper_mixin import CaregiverContactModelWrapperMixin
from .cohort_schedules_model_wrapper_mixin import CohortSchedulesModelWrapperMixin


class CaregiverCohortModelWrapper(CaregiverLocatorModelWrapperMixin,
                                  CaregiverContactModelWrapperMixin,
                                  CohortSchedulesModelWrapperMixin,
                                  ModelWrapper):

    model = 'flourish_caregiver.cohort'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'cohort_switch_listboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier']

    @property
    def subject_identifier(self):
        return self.object.subject_identifier
