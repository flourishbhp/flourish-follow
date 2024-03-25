from django.apps import apps as django_apps
from edc_base.utils import get_utcnow
from edc_constants.constants import YES

from .caregiver_contact_model_wrapper import ContactModelWrapper


class CaregiverContactModelWrapperMixin:

    contact_model_wrapper_cls = ContactModelWrapper

    @property
    def caregiver_contact_cls(self):
        return django_apps.get_model('flourish_follow.contact')

    @property
    def caregiver_contacts(self):
        """ Participant can have more than one contact entry
        """
        wrapped_contacts = []
        model_objs = self.caregiver_contact_cls.objects.filter(
            **self.caregiver_contact_options).order_by('-contact_datetime')[:5]
        for obj in model_objs:
            wrapped_contacts.append(
                self.contact_model_wrapper_cls(obj))
        return wrapped_contacts

    @property
    def latest_caregiver_contact(self):
        try:
            model_obj = self.caregiver_contact_cls.objects.filter(
                **self.caregiver_contact_options).latest(
                    'contact_datetime', 'report_datetime')
        except self.caregiver_contact_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def caregiver_contact(self):
        """Returns a wrapped unsaved caregiver contact.
        """
        model_obj = self.caregiver_contact_cls(
            **self.create_caregiver_contact_options)
        return self.contact_model_wrapper_cls(model_obj=model_obj)

    @property
    def create_caregiver_contact_options(self):
        """Returns a dictionary of options to create a new
        unpersisted caregiver contact model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options

    @property
    def caregiver_contact_options(self):
        """Returns a dictionary of options to get an existing
        caregiver contact model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options

    @property
    def successful_contact(self):
        return self.caregiver_contact_cls.objects.filter(
            **self.caregiver_contact_options,
            contact_success=YES,
            appt_scheduled=YES,
            appt_date__isnull=False, ).exists()

    @property
    def is_past_scheduled_dt(self):
        appt_dt = getattr(self.latest_caregiver_contact, 'appt_date', None)
        return appt_dt <= get_utcnow().date() if appt_dt else False
