# from django.core.exceptions import ValidationError
# from django.test import TestCase
# from edc_base.utils import get_utcnow
# from edc_constants.constants import YES
# 
# from ..form_validations import LogEntryFormValidator
# from .models import CaregiverLocator
# 
# 
# class TestLogEntryValidatorForm(TestCase):
# 
#     def setUp(self):
#         CaregiverLocator.objects.create(
#             study_maternal_identifier='123-4',
#             screening_identifier='12',
#             locator_date=get_utcnow().date(),
#             may_call=YES,
#             subject_cell='71234567',
#             subject_phone='74720123')
# 
#         self.options = {
#             'phone_num_type': ['subject_cell', ],
#             'phone_num_success': ['subject_cell', 'subject_cell_alt'],
#         }
# 
#     def test_contact_success_valid(self):
#         """
#         Checks form saves successfully with all necessary field
#         values completed.
#         """
#         form_validator = LogEntryFormValidator(cleaned_data=self.options)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
