from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .caregiver_cohort_model_wrapper_mixin import CaregiverCohortModelWrapperMixin

class ContactModelWrapper(CaregiverCohortModelWrapperMixin,
                          ModelWrapper):

    model = 'flourish_follow.contact'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'cohort_switch_listboard_url')
    next_url_attrs = ['subject_identifier', 'cohort_name']
    querystring_attrs = ['subject_identifier', ]
