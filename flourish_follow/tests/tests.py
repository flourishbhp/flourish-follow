from django.test.testcases import TestCase
from edc_base.utils import get_utcnow
from model_mommy import mommy

from ..models import Call, WorkList, Log
from dateutil.relativedelta import relativedelta


class TestCallManager(TestCase):

    def setUp(self):
        self.logentry_options = {
            'study_maternal_identifier': '035-123456',
            'call_datetime': get_utcnow(),
            'phone_num_type': ['subject_cell'],
            'phone_num_success': ['subject_cell']}

    def test_create_registered_model(self):
        """Test if a start model created a call instance.
        """
        WorkList.objects.create(study_maternal_identifier='035-123456')
        self.assertEqual(Call.objects.filter(subject_identifier='035-123456').count(), 1)  

    def test_multiple_logentries_sameday(self):
        """Test if collecting more than 1 call log entry in the same date will
            allow, and schedule next call."""
        WorkList.objects.create(study_maternal_identifier='035-123456')
        first_call = Call.objects.filter(
            subject_identifier='035-123456').latest('scheduled')
        log = Log.objects.create(call=first_call)
        self.logentry_options.update(log=log)
        mommy.make_recipe('flourish_follow.logentry', **self.logentry_options)
        self.assertEqual(
            Call.objects.filter(
                subject_identifier='035-123456', call_status='NEW').count(), 1)
        second_call = Call.objects.filter(
            subject_identifier='035-123456').latest('scheduled')
        log = Log.objects.create(call=second_call)
        mommy.make_recipe('flourish_follow.logentry',
                          log=log, call_datetime=get_utcnow() + relativedelta(minutes=1))
        self.assertEqual(
            Call.objects.filter(
                subject_identifier='035-123456', call_status='NEW').count(), 1)
        next_schedule_date = (get_utcnow() + relativedelta(days=1)).date()
        self.assertEqual(
            Call.objects.filter(
                subject_identifier='035-123456', scheduled__date=next_schedule_date).count(), 2)
