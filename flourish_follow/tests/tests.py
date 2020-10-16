from django.apps import apps as django_apps
from django.test.testcases import TestCase

from edc_call_manager.caller_site import site_model_callers

from ..models.worklist import WorkList

Call = django_apps.get_model('edc_call_manager', 'call')
Log = django_apps.get_model('edc_call_manager', 'log')
LogEntry = django_apps.get_model('edc_call_manager', 'logentry')


class TestCallManager(TestCase):

    def setUp(self):
        pass
 
    def test_create_registered_model(self):
        """Testt if a start model created a call instance.
        """
        WorkList.objects.create(
            study_maternal_identifier='035-123456')
        self.assertEqual(Call.objects.filter(subject_identifier='035-123456').count(), 1)  
