from django.apps import apps as django_apps

class CaregiverCohortModelWrapperMixin:

    cohort_model_wrapper_cls = None

    @property
    def caregiver_cohort_cls(self):
        return django_apps.get_model('flourish_caregiver.cohort')

    @property
    def caregiver_cohort_obj(self):
        try:
            return self.caregiver_cohort_cls.objects.get(
                **self.caregiver_cohort_options)
        except self.caregiver_cohort_cls.DoesNotExist:
            return None

    @property
    def caregiver_cohort(self):
        """ Returns a wrapped saved or unsaved caregiver cohort instance
        """
        model_obj = self.caregiver_cohort_obj or self.caregiver_cohort_cls(
            **self.create_caregiver_cohort_options)
        return self.cohort_model_wrapper_cls(model_obj=model_obj)

    @property
    def create_caregiver_cohort_options(self):
        """ Returns a dictionary of options to create a new
            unpersisted caregiver cohort model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options

    @property
    def caregiver_cohort_options(self):
        """ Returns a dictionary of options to get an existing
            caregiver cohort model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            current_cohort=True)
        return options

    @property
    def cohort_name(self):
        return getattr(self.caregiver_cohort_obj, 'name', None)
