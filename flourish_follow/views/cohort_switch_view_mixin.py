from django.apps import apps as django_apps
from django.db import transaction
from django.db.models import OuterRef, Exists, Q
from django.shortcuts import redirect
from django.urls import reverse
from edc_base.utils import get_utcnow
from edc_constants.constants import MALE, FEMALE, YES, NO

from flourish_caregiver.helper_classes import SequentialCohortEnrollment

class SqCohortEnrollment(SequentialCohortEnrollment):
    """ Inherints from sequential enrollment class, and re-defines onschedule methods
        to cater for immediate FU schedule enrollment on cohort C primary aims.
    """
    @property
    def evaluated_cohort(self):
        return 'cohort_c'

    def put_child_onschedule(self):
        child_fu_model, child_fu_name = self.get_child_fu_details('cohort_c')

        self.put_on_schedule(onschedule_model=child_fu_model,
                             schedule_name=child_fu_name,
                             base_appt_datetime=get_utcnow(),
                             subject_identifier=self.child_subject_identifier, )

    def put_caregiver_onschedule(self):
        child_count = str(self.child_consent_obj.caregiver_visit_count)
        caregiver_fu_model, caregiver_fu_name = self.get_caregiver_fu_details(
            'cohort_c', child_count)

        self.put_on_schedule(onschedule_model=caregiver_fu_model,
                             schedule_name=caregiver_fu_name,
                             base_appt_datetime=get_utcnow(),
                             subject_identifier=self.caregiver_subject_identifier,
                             is_caregiver=True, )

    def switch_to_cohort_c(self):
        """ Calls the `put_onschedule` method to enrol participant on cohort_c
            FU schedule.
        """

        cohort_obj = self.create_cohort_instance()
        if cohort_obj:
            try:
                with transaction.atomic():
                    self.put_onschedule()
            except Exception as e:
                raise e
            self.resave_cohort_instances()

    def resave_cohort_instances(self):
        """ Save each cohort instance for the subject identifier to update
            variables computed on_save of the model.
        """
        cohorts = self.cohort_model_cls.objects.filter(
            subject_identifier=self.child_subject_identifier)
        for cohort in cohorts:
            cohort.save()

class CohortCHEUSwitchViewMixin:

    child_offstudy_model = 'flourish_prn.childoffstudy'
    maternal_dataset_model = 'flourish_caregiver.maternaldataset'

    @property
    def child_offstudy_model_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def maternal_dataset_model_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    @property
    def child_offstudy_pids(self):
        offstudy = self.child_offstudy_model_cls.objects.values_list(
            'subject_identifier', flat=True)
        return list(set(offstudy))

    @property
    def contact_cls(self):
        return django_apps.get_model('flourish_follow.contact')

    @property
    def no_contact_pids(self):
        """ Returns subject identifier(s) for participant's contacted
            but did not agree to being scheduled for a FU appointment.
        """
        no_contact = self.contact_cls.objects.filter(
            appt_scheduled=NO).values_list(
                'subject_identifier', flat=True)
        return list(set(no_contact))

    @property
    def successful_pids(self):
        """ Returns subject identifier(s) for participant's contacted
            sucessfully and scheduled a FU appointment.
        """
        successful_pids = self.contact_cls.objects.filter(
            contact_success=YES,
            appt_scheduled=YES,
            appt_date__isnull=False, ).values_list(
                'subject_identifier', flat=True)
        return list(set(successful_pids))
        

    @property
    def categories_filter(self):
        """ Participant's to be moved from secondary to primary aims:
            2 participant's from group(s) BMI: <14.9 and Age: [9.5, 14) Gender: Male
            5 participant's from group(s) BMI: 15-17.9 and Age: [14, 17) Gender: Male
            1 participant's from group(s) BMI: >18 and Age: [9.5, 14) Gender: Female
            5 participant's from group(s) BMI: >18 and Age: [9.5, 14) Gender: Male
            6 participant's from group(s) BMI: >18 and Age: [14, 17) Gender: Male
        """
        return [
            {'limit': 2, 'bmi_range': (0, 14.9), 'age_range': (9.5, 14), 'gender': MALE},
            {'limit': 5, 'bmi_range': (15, 17.9), 'age_range': (14, 17), 'gender': MALE},
            {'limit': 1, 'bmi_range': (18, float('inf')), 'age_range': (9.5, 14), 'gender': FEMALE},
            {'limit': 5, 'bmi_range': (18, float('inf')), 'age_range': (9.5, 14), 'gender': MALE},
            {'limit': 6, 'bmi_range': (18, float('inf')), 'age_range': (14, 17), 'gender': MALE}]

    def filter_condition(self, obj, category):
        """ Apply matrix category filter to the queryset.
        """
        child_age, child_bmi, child_gender = obj.child_age, obj.child_bmi, obj.child_gender
        if not all([child_age, child_bmi, child_gender, ]):
            return False
        return (child_age >= category['age_range'][0] and
                child_age < category['age_range'][1] and
                child_gender == category['gender'] and
                child_bmi >= category['bmi_range'][0] and
                child_bmi <= category['bmi_range'][1])

    def is_eligible(self, cohort_obj):
        """ Check if participant is eligible for cohort C primary,
            3-drug ART for HEU
        """
        child_dataset = getattr(
            cohort_obj.caregiver_child_consent, 'child_dataset', None)
        try:
            maternal_dataset_obj = self.maternal_dataset_model_cls.objects.get(
                study_maternal_identifier=getattr(
                    child_dataset, 'study_maternal_identifier', None))
        except self.maternal_dataset_model_cls.DoesNotExist:
            return False
        else:
            arv_regimen = getattr(
                maternal_dataset_obj, 'mom_pregarv_strat', None)
            return arv_regimen == '3-drug ART'
        

    def get_queryset(self):
        """ Filter participant's enrolled into cohort C sec and align with a specific
            matrix category, if they have never been called and declined FU.
            @return: filtered queryset objects 
        """
        filtered_list = []
        queryset = super().get_queryset()
        
        # Filter queryset for participants currently in cohort C sec,
        # and don't have a previous cohort C instance.
        subquery = self.model_cls.objects.filter(
            subject_identifier=OuterRef('subject_identifier'),
            name='cohort_c').values('subject_identifier')

        exclude_pids = self.child_offstudy_pids
        exclude_pids.extend(self.no_contact_pids)
        queryset = queryset.exclude(
            Q(subject_identifier__in=exclude_pids))

        # Removes participants on above described condition, unless participant
        # is already contacted and switched cohorts.
        queryset = queryset.annotate(
            has_cohort_c=Exists(subquery)).filter(
                (Q(name='cohort_c_sec', current_cohort=True) & ~Q(has_cohort_c=True)) | Q(
                    subject_identifier__in=self.successful_pids, current_cohort=True),
                exposure_status='EXPOSED',)


        for category in self.categories_filter:
            result = []
            _count = 0
            for obj in queryset:
                if not self.is_eligible(obj):
                    continue
                if _count >= category['limit']:
                    break
                elif self.filter_condition(obj, category):
                    result.append(obj.id)
                    _count += 1
            filtered_list.extend(result)

        return queryset.filter(id__in=filtered_list)


def switch_cohort_redirect(request, subject_identifier):
    helper_cls = SqCohortEnrollment(
        child_subject_identifier=subject_identifier)
    helper_cls.switch_to_cohort_c()
    return redirect(reverse('flourish_dashboard:child_dashboard_url',
                            kwargs={'subject_identifier': subject_identifier}))
