from edc_constants.constants import YES
from edc_form_validators import FormValidator


class FUContactFormValidator(FormValidator):

    def clean(self):
        fields_applicable = ['appt_scheduled',
                             'continue_contact']

        for field_applicable in fields_applicable:
            self.applicable_if(
                YES,
                field='contact_success',
                field_applicable=field_applicable)

        self.required_if(
            YES,
            field='appt_scheduled',
            field_required='appt_date')
