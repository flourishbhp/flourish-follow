from django.apps import apps as django_apps


class CohortSchedulesModelWrapperMixin:

    cohort_schedules_model = 'flourish_caregiver.cohortschedules'
    child_appointment_model = 'flourish_child.appointment'

    @property
    def cohort_schedules_model_cls(self):
        return django_apps.get_model(self.cohort_schedules_model)

    @property
    def child_appointment_model_cls(self):
        return django_apps.get_model(self.child_appointment_model)

    @property
    def has_fu_appts(self):
        schedule_names = self.cohort_schedules_model_cls.objects.filter(
            cohort_name=self.name,
            schedule_type__icontains='followup',
            onschedule_model__startswith='flourish_child').values_list(
                'schedule_name', flat=True)
        fu_exists = self.child_appointment_model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            schedule_name__in=schedule_names).exists()
        return fu_exists
