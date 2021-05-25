from edc_constants.constants import OTHER
from edc_form_validators import FormValidator

from .contact_form_validator import ContactFormValidator


class HomeVisitFormValidator(ContactFormValidator, FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
        study_maternal_identifier = cleaned_data.get('study_maternal_identifier')

        contact_location = cleaned_data.get('contact_location')

        successful_location = cleaned_data.get('successful_location')

        if successful_location and contact_location:
            self.validate_success_selection(
                'successful_location', contact_location, successful_location,
                study_maternal_identifier)

            fields_map = {'physical_address': 'phy_addr_unsuc',
                          'subject_work_place': 'workplace_unsuc',
                          'indirect_contact_physical_address': 'contact_person_unsuc'}

            self.validate_unsuccesful_na(
                fields_map, contact_location, successful_location)

        self.required_if(
            OTHER,
            field='phy_addr_unsuc',
            field_required='phy_addr_unsuc_other')

        self.required_if(
            OTHER,
            field='workplace_unsuc',
            field_required='workplace_unsuc_other')

        self.required_if(
            OTHER,
            field='contact_person_unsuc',
            field_required='contact_person_unsuc_other')
