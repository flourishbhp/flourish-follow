from django.conf import settings
from edc_model_wrapper import ModelWrapper
from flourish_dashboard.model_wrappers.caregiver_locator_model_wrapper_mixin import (
    CaregiverLocatorModelWrapperMixin)

from .caregiver_contact_model_wrapper_mixin import CaregiverContactModelWrapperMixin


class CaregiverCohortModelWrapper(CaregiverLocatorModelWrapperMixin,
                                  CaregiverContactModelWrapperMixin,
                                  ModelWrapper):

    model = 'flourish_caregiver.cohort'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'cohort_switch_listboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier']

    @property
    def contacts(self):
        if self.locator_model_obj:
            contacts = [
                self.locator_model_obj.subject_cell or '',
                self.locator_model_obj.subject_cell_alt or '',
                self.locator_model_obj.subject_phone or '',
                self.locator_model_obj.subject_phone_alt or '']
            return ', '.join(list(filter(None, contacts)))
        return None
