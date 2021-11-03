from django.apps import apps as django_apps
from edc_constants.constants import NO, YES, CLOSED, OTHER
from edc_form_validators import FormValidator

from .contact_form_validator import ContactFormValidator
from django.core.exceptions import ValidationError


class LogEntryFormValidator(ContactFormValidator, FormValidator):

    @property
    def caregiver_locator_cls(self):
        return django_apps.get_model('flourish_caregiver.caregiverlocator')

    def clean(self):
        cleaned_data = self.cleaned_data
        study_maternal_identifier = cleaned_data.get('study_maternal_identifier')

        contact_used = cleaned_data.get('phone_num_type')

        contact_success = cleaned_data.get('phone_num_success')

        if contact_success and contact_used:
            self.validate_success_selection(
                'phone_num_success', contact_used, contact_success, study_maternal_identifier)

            fields_map = {'subject_cell': 'cell_contact_fail',
                          'subject_cell_alt': 'alt_cell_contact_fail',
                          'subject_phone': 'tel_contact_fail',
                          'subject_phone_alt': 'alt_tel_contact_fail',
                          'subject_work_phone': 'work_contact_fail',
                          'indirect_contact_cell': 'cell_alt_contact_fail',
                          'indirect_contact_phone': 'tel_alt_contact_fail',
                          'caretaker_cell': 'cell_resp_person_fail',
                          'caretaker_tel': 'tel_resp_person_fail'}

            self.validate_unsuccesful_na(fields_map, contact_used, contact_success)

        self.required_if(YES,
                         field='appt',
                         field_required='appt_type')

        self.validate_other_specify(field='appt_type',
                                    other_specify_field='other_appt_type')

        self.required_if(
            NO,
            field='appt',
            field_required='appt_reason_unwilling')

        fields = ['appt_date', 'appt_grading', 'appt_location']
        for field in fields:
            self.required_if(
                YES,
                field='appt',
                field_required=field)

        self.m2m_other_specify(
            OTHER,
            m2m_field='appt_reason_unwilling',
            field_other='appt_reason_unwilling_other')

        self.validate_other_specify(field='appt_location')

        self.not_applicable_if(
            ['none_of_the_above'],
            field='phone_num_success',
            field_applicable='appt')

        self.validate_other_specify(field='home_visit')

        call = cleaned_data.get('log').call
        self.validate_closed_call(call)

    def validate_closed_call(self, call_model):
        if call_model.call_status == CLOSED:
            raise ValidationError('This call is already closed.')
