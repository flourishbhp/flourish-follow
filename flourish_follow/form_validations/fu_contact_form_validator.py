from django import forms
from edc_constants.constants import YES
from edc_form_validators import FormValidator


class FUContactFormValidator(FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
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

        appt_dt = cleaned_data.get('appt_date', None)
        final_contact = cleaned_data.get('final_contact', None)

        if appt_dt and final_contact == YES:
            raise forms.ValidationError(
                {'final_contact':
                 'An appointment has been scheduled, participant will '
                 'continue being contacted.'})
