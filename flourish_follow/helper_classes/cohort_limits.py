from django.apps import apps as django_apps
from edc_constants.constants import NO


class CohortLimitsMixin:

    cohort_model = 'flourish_caregiver.cohort'
    subject_schedule_history_model = 'edc_visit_schedule.subjectschedulehistory'
    cohort_schedules_model = 'flourish_caregiver.cohortschedules'

    @property
    def cohort_model_cls(self):
        return django_apps.get_model(self.cohort_model)

    @property
    def subject_schedule_history_cls(self):
        return django_apps.get_model(self.subject_schedule_history_model)

    @property
    def cohort_schedules_model_cls(self):
        return django_apps.get_model(self.cohort_schedules_model)

    def get_fu_schedule_names(self, cohort_name):
        """
            Return child FU schedule_names for a specific cohort
        """
        return self.cohort_schedules_model_cls.objects.filter(
            cohort_name=cohort_name,
            schedule_type__in=['followup', 'sq_followup', ],
            child_count__isnull=True).values_list(
                'schedule_name', flat=True)

    def cohort_b_current_counts(self, per_crf_counts={}):
        """ This uses the neuro-behavioural assessments to determine current
            completed counts. i.e. PennCNB, CBCL, or Brief2-Parent report
            limits: {'EXPOSED': 200, 'UNEXPOSED': 100}
        """
        neuro_crfs = ['childpenncnb', 'childcbclsection1', 'brief2parent']
        pidx_completed = set()
        for crf in neuro_crfs:
            model_cls = django_apps.get_model(f'flourish_child.{crf}')
            qs = model_cls.objects.all()
            if crf == 'childpenncnb':
                qs = qs.exclude(completed=NO)
            childidx = qs.values_list(
                'child_visit__subject_identifier', flat=True)
            per_crf_counts.update({f'{crf}': set(childidx)})
            pidx_completed.update(childidx)

        return self.get_exposure_counts(pidx_completed)

    def cohort_c_current_counts(self):
        """ This evaluates the number of follow-up visits completed for cohort
            C. This will determine the cardiometabolics assessment limits
            limits: {'EXPOSED': 100, 'UNEXPOSED': 200}
        """
        schedule_names = self.get_fu_schedule_names(cohort_name='cohort_c')

        childidx = self.subject_schedule_history_cls.objects.filter(
            schedule_name__in=schedule_names).values_list(
                'subject_identifier', flat=True)
        childidx = set(childidx)

        return self.get_exposure_counts(childidx)

    def get_neuro_crf_breakdown(self, neuro_crf_childidx={}):
        breakdown = {}
        for crf, childidx in neuro_crf_childidx.items():
            heu_count, huu_count = self.get_exposure_counts(childidx)
            breakdown[crf] = (heu_count, huu_count)
        return breakdown

    def get_exposure_counts(self, childidx):
        """ Get counts for each exposure status for child PIDs provided.
        """
        heu_count = 0
        huu_count = 0
        for childid in childidx:
            latest_cohort = self.cohort_model_cls.objects.filter(
                subject_identifier=childid).latest('assign_datetime')
            if latest_cohort.exposure_status == 'EXPOSED':
                heu_count += 1
            elif latest_cohort.exposure_status == 'UNEXPOSED':
                huu_count += 1
        return heu_count, huu_count

    def check_limits_reached(self, cohort_name, exclude_status):
        cohort_limits = {'cohort_b': [('EXPOSED', 200), ('UNEXPOSED', 100)],
                         'cohort_c': [('EXPOSED', 100), ('UNEXPOSED', 200)]}
        limits = cohort_limits.get(cohort_name, [])

        current_heu_count = None
        current_huu_count = None
        if cohort_name == 'cohort_b':
            current_heu_count, current_huu_count = self.cohort_b_current_counts()
        elif cohort_name == 'cohort_c':
            current_heu_count, current_huu_count = self.cohort_c_current_counts()

        current_counts = {
            'EXPOSED': current_heu_count,
            'UNEXPOSED': current_huu_count}

        for limit in limits:
            exposure_status, _count = limit

            if current_counts.get(exposure_status) >= _count:
                exclude_status.append(exposure_status)
