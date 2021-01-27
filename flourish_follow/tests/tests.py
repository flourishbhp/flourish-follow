from django.test.testcases import TestCase

from ..models import Call, WorkList


class TestCallManager(TestCase):

    def setUp(self):
        pass
 
    def test_create_registered_model(self):
        """Testt if a start model created a call instance.
        """
        WorkList.objects.create(study_maternal_identifier='035-123456')
        self.assertEqual(Call.objects.filter(subject_identifier='035-123456').count(), 1)  
