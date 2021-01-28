from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES, NOT_APPLICABLE
from edc_form_validators import FormValidator


class LogEntryFormValidator(FormValidator):

    @property
    def caregiver_locator_cls(self):
        return django_apps.get_model('flourish_caregiver.caregiverlocator')

    def clean(self):
        cleaned_data = self.cleaned_data
        study_maternal_identifier = cleaned_data.get('study_maternal_identifier')

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

        self.validate_other_specify(field='appt_reason_unwilling')

        self.validate_other_specify(field='appt_location')

        contact_used = cleaned_data.get('phone_num_type')
            
        contact_success = cleaned_data.get('phone_num_success')
        print(contact_success, contact_used, '##############')
        if contact_success and contact_used:
            if not 'none_of_the_above' in contact_success:
                if not set(contact_success).issubset(set(contact_used)):
                    contacts = []
                    diff = [item for item in contact_success if item not in contact_used]
                    for item in diff:
                        locator_obj = self.caregiver_locator(study_maternal_identifier)
                        contacts.append(getattr(locator_obj, item))
                    msg = {'phone_num_success':
                           f'{", ".join(contacts)} have not been used for contact so can not '
                           'be selected as successful in reaching'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

            fields_map = {
                'subject_cell': 'cell_contact_fail',
                'subject_cell_alt': 'alt_cell_contact_fail',
                'subject_phone': 'tel_contact_fail',
                'subject_phone_alt': 'alt_tel_contact_fail',
                'subject_work_phone': 'work_contact_fail',
                'indirect_contact_cell': 'cell_alt_contact_fail',
                'indirect_contact_phone': 'tel_alt_contact_fail',
                'caretaker_cell': 'cell_resp_person_fail',
                'caretaker_tel': 'tel_resp_person_fail'}

            unsuccessful = [item for item in contact_used if item not in contact_success]

            for field_attr in unsuccessful:
                field = fields_map.get(field_attr)
                if field in cleaned_data and cleaned_data.get(field) == NOT_APPLICABLE:
                    msg = {field: 'This field is applicable'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

            for field_attr in contact_success:
                field = fields_map.get(field_attr)
                if field in cleaned_data and cleaned_data.get(field) != NOT_APPLICABLE:
                    msg = {field: 'This field is not applicable'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

            not_applicable = [fields_map.get(na) for na in fields_map.keys() if na not in contact_used]
            for field in not_applicable:
                if field in cleaned_data and cleaned_data.get(field) != NOT_APPLICABLE:
                    msg = {field: 'This field is not applicable'}
                    self._errors.update(msg)
                    raise ValidationError(msg)

    def caregiver_locator(self, study_maternal_identifier):
        try:
            locator = self.caregiver_locator_cls.objects.get(
                study_maternal_identifier=study_maternal_identifier)
        except self.caregiver_locator_cls.DoesNotExist:
            raise ValidationError(
                f'Caregiver locator for {study_maternal_identifier} does not exist.')
        else:
            return locator
