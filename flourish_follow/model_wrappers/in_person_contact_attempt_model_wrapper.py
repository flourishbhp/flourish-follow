from django.conf import settings

from edc_model_wrapper.wrappers import ModelWrapper


class InPersonContactAttemptModelWrapper(ModelWrapper):

    model = 'flourish_follow.inpersoncontactattempt'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'flourish_follow_listboard_url')
    querystring_attrs = ['in_person_log']
    next_url_attrs = ['study_maternal_identifier']

    @property
    def study_maternal_identifier(self):
        return self.object.study_maternal_identifier

    @property
    def in_person_log(self):
        return self.object.in_person_log.id
