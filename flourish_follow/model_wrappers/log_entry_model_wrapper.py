from django.conf import settings
from edc_model_wrapper import ModelWrapper


class LogEntryModelWrapper(ModelWrapper):

    model = 'flourish_follow.logentry'
    querystring_attrs = ['log', 'study_maternal_identifier']
    next_url_attrs = ['log', 'study_maternal_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get('flourish_follow_listboard_url')
