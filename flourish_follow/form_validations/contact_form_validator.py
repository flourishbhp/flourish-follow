from django.core.exceptions import ValidationError
from edc_constants.constants import NOT_APPLICABLE


class ContactFormValidator:

    def validate_success_selection(
            self, success_field, contact_used, contact_success, identifier):
        if not ('none_of_the_above' in contact_success):
            if not set(contact_success).issubset(set(contact_used)):
                contacts = []
                diff = [item for item in contact_success if item not in contact_used]
                for item in diff:
                    locator_obj = self.caregiver_locator(identifier)
                    contacts.append(getattr(locator_obj, item))
                msg = {success_field:
                       f'{", ".join(contacts)} have not been used for contact so can not '
                       'be selected as successful.'}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            if len(contact_success) > 1:
                msg = {success_field:
                       'None of the above can not be combined with other selections.'}
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

    def validate_unsuccesful_na(self, fields_map, contact_used, contact_success):
        cleaned_data = self.cleaned_data

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
