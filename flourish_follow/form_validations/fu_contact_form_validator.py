from django import forms
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator


class FUContactFormValidator(FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data

        self.applicable_if(
            YES,
            field='contact_success',
            field_applicable='appt_scheduled')

        self.required_if(
            YES,
            field='appt_scheduled',
            field_required='appt_date')

        appt_dt = cleaned_data.get('appt_date', None)
        final_contact = cleaned_data.get('final_contact', None)
        contact_success = cleaned_data.get('contact_success', None)

        if appt_dt and final_contact == NO:
            raise forms.ValidationError(
                {'final_contact':
                 'An appointment has been scheduled, participant will '
                 'not be contacted again.'})
        elif contact_success == NO and final_contact == YES:
            raise forms.ValidationError(
                {'final_contact':
                 'Participant has not yet been reached.'})
