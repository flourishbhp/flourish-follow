from django.apps import apps as django_apps


class FollowUtils:
    caregiver_offstudy_model = 'flourish_prn.caregiveroffstudy'
    
    @property
    def caregiver_offstudy_model_cls(self):
        return django_apps.get_model(self.caregiver_offstudy_model)
    
    def caregivers_offstudy(self):
        pids = self.caregiver_offstudy_model_cls.objects.values_list(
            'subject_identifier', flat=True)
        return pids

follow_utils = FollowUtils()
