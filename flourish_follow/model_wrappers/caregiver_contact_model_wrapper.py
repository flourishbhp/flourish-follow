from django.conf import settings
from edc_model_wrapper import ModelWrapper


class ContactModelWrapper(ModelWrapper):
    model = 'flourish_follow.contact'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'cohort_switch_listboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier']
