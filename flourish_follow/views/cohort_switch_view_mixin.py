from django.apps import apps as django_apps
from django.db import transaction
from django.db.models import Case, Exists, IntegerField, OuterRef, Q, Subquery, Value, When
from django.shortcuts import redirect
from django.urls import reverse
from edc_base.utils import get_utcnow
from edc_constants.constants import MALE, FEMALE, YES, NO

from flourish_caregiver.helper_classes import SequentialCohortEnrollment
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Now


class SqCohortEnrollment(SequentialCohortEnrollment):
    """ Inherints from sequential enrollment class, and re-defines onschedule methods
        to cater for immediate FU schedule enrollment.
    """

    def __init__(self, child_subject_identifier=None, child_cohort_name=None):
        self.child_subject_identifier = child_subject_identifier
        self.child_cohort_name = child_cohort_name

    @property
    def evaluated_cohort(self):
        return self.child_cohort_name

    def put_child_onschedule(self):
        child_fu_model, child_fu_name = self.get_child_fu_details(
            self.child_cohort_name)

        self.put_on_schedule(onschedule_model=child_fu_model,
                             schedule_name=child_fu_name,
                             base_appt_datetime=get_utcnow(),
                             subject_identifier=self.child_subject_identifier, )

    def put_caregiver_onschedule(self):
        child_count = str(self.child_consent_obj.caregiver_visit_count)
        caregiver_fu_model, caregiver_fu_name = self.get_caregiver_fu_details(
            self.child_cohort_name, child_count)

        self.put_on_schedule(onschedule_model=caregiver_fu_model,
                             schedule_name=caregiver_fu_name,
                             base_appt_datetime=get_utcnow(),
                             subject_identifier=self.caregiver_subject_identifier,
                             is_caregiver=True, )

    def enrol_for_fu_schedule(self):
        """ Calls the `put_onschedule` method to enrol participant on FU schedule.
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
    child_visit_model = 'flourish_child.childvisit'
    child_dummy_consent_model = 'flourish_child.childdummysubjectconsent'
    subject_schedule_history_model = 'edc_visit_schedule.subjectschedulehistory'

    @property
    def child_dummy_consent_model_cls(self):
        return django_apps.get_model(self.child_dummy_consent_model)

    @property
    def child_offstudy_model_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def maternal_dataset_model_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    @property
    def subject_schedule_history_cls(self):
        return django_apps.get_model(self.subject_schedule_history_model)

    @property
    def child_offstudy_pids(self):
        offstudy = self.child_offstudy_model_cls.objects.values_list(
            'subject_identifier', flat=True)
        return list(set(offstudy))

    @property
    def contact_cls(self):
        return django_apps.get_model('flourish_follow.contact')

    @property
    def child_visit_cls(self):
        return django_apps.get_model(self.child_visit_model)

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
    def fu_appt_done(self):
        fu_pids = self.child_visit_cls.objects.filter(
            schedule_name__icontains='fu').values_list(
                'subject_identifier', flat=True)
        return list(set(fu_pids))

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

    def child_age_lt_18months(self, queryset):
        """ Filter out participant's who are less than 18 months of age
            they are not eligible for FU yet.
            @param queryset: cohort queryset objects
            @return: filtered list of cohort instances
        """
        lt_pids = [obj.subject_identifier for obj in queryset if (obj.child_age or 0) < 1.5]
        return lt_pids

    def get_queryset(self):
        """ 1. Filter participant's enrolled into cohort C sec and align with a specific
            matrix category, if they have never been called and declined FU.
            2. If there's a cohort name filter, returns participant's within a specific
            cohort if they haven't done their FU yet.
            3. For cohort_a participants' returns only participants eligible for FUs i.e.
            18months or older (1.5 in years).
            @return: filtered queryset objects 
        """
        filtered_list = []
        queryset = super().get_queryset()

        filter_options = self.get_queryset_filter_options(
            self.request, *self.args, **self.kwargs)
        exclude_pids = self.child_offstudy_pids

        cohort_name = filter_options.get('name', '')
        if cohort_name:
            
            exclude_pids.extend(self.fu_appt_done)
            queryset = queryset.filter(
                name=cohort_name, current_cohort=True,).exclude(
                    subject_identifier__in=exclude_pids)

            queryset = queryset.exclude(
                subject_identifier__in=self.child_age_lt_18months(queryset))
            
        else:
            # Filter queryset for participants currently in cohort C sec,
            # and don't have a previous cohort C instance.
            subquery = self.model_cls.objects.filter(
                subject_identifier=OuterRef('subject_identifier'),
                name='cohort_c').values('subject_identifier')
    
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
    
            queryset = queryset.filter(id__in=filtered_list)
        queryset = self.order_queryset(queryset)
        return queryset


    def order_queryset(self, queryset):
        """ Order queryset objects by age and if already on FU i.e. push
            participants who have already been enrolled on FU to the bottom of list.
        """
        # Order queryset by age
        dob_subquery = self.child_dummy_consent_model_cls.objects.filter(
            subject_identifier=OuterRef('subject_identifier')).values('dob')[:1]
        age_expression = ExpressionWrapper(
            Now() - Subquery(dob_subquery),
            output_field=IntegerField())

        # Subquery to check if participant is enrolled on FU schedule
        has_fu_subquery = self.subject_schedule_history_cls.objects.filter(
            subject_identifier=OuterRef('subject_identifier'),
            schedule_name__icontains='fu').values('subject_identifier')

        # Case statement to assign an integer value based on the existence of a FU
        order_by_fu = Case(
            When(subject_identifier__in=has_fu_subquery, then=Value(1)),
            default=Value(0),
            output_field=IntegerField())

        queryset = queryset.annotate(
            age=age_expression,
            has_fu=order_by_fu, ).order_by('has_fu', '-age')
            
        return queryset


def cohort_fu_enrol_redirect(request, subject_identifier, cohort_name, enrol_cohort):
    """ Set parameters cohort_name, enrol_cohort manually for participant's being pulled
        from cohort_c_sec to the primary cohort c aims.
    """
    enrol_cohort = False if cohort_name == 'cohort_c_sec' else bool(int(enrol_cohort)) 
    cohort_name = 'cohort_c' if cohort_name == 'cohort_c_sec' else cohort_name

    if enrol_cohort:
        url = reverse('flourish_dashboard:child_dashboard_url',
                      kwargs={'subject_identifier': subject_identifier})
        url = f'{url}fu_enrollment'
    else:
        helper_cls = SqCohortEnrollment(
            child_subject_identifier=subject_identifier,
            child_cohort_name=cohort_name)
        helper_cls.enrol_for_fu_schedule()
        url = reverse('flourish_dashboard:child_dashboard_url',
                      kwargs={'subject_identifier': subject_identifier})
    return redirect(url)
