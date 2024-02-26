from django.apps import apps as django_apps
from django.db.models import OuterRef, Exists, Q
from edc_constants.constants import MALE, FEMALE, NO, YES


class CohortCHEUSwitchViewMixin:

    child_offstudy_model = 'flourish_prn.childoffstudy'

    @property
    def child_offstudy_model_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def child_offstudy_pids(self):
        offstudy = self.child_offstudy_model_cls.objects.values_list(
            'subject_identifier', flat=True)
        return list(set(offstudy))

    @property
    def no_contact_pids(self):
        contact_cls = django_apps.get_model('flourish_follow.contact')
        no_contact = contact_cls.objects.filter(
            appt_scheduled=NO, final_contact=YES).values_list(
                'subject_identifier', flat=True)
        return list(set(no_contact))
        

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

    def get_queryset(self):
        """ Filter participant's enrolled into cohort C sec and align with a specific
            matrix category, if they have never been called and declined FU.
            @return: filtered queryset objects 
        """
        filtered_list = []
        queryset = super().get_queryset()
        
        # Filter queryset for participants currently in cohort C sec, and don't have a previous cohort C
        # instance.
        subquery = self.model_cls.objects.filter(
            subject_identifier=OuterRef('subject_identifier'),
            name='cohort_c').values('subject_identifier')

        exclude_pids = self.child_offstudy_pids
        exclude_pids.extend(self.no_contact_pids)
        queryset = queryset.exclude(
            Q(subject_identifier__in=exclude_pids))

        queryset = queryset.annotate(
            has_cohort_c=Exists(subquery)).filter(
                Q(name='cohort_c_sec') & ~Q(has_cohort_c=True),
                current_cohort=True,
                exposure_status='EXPOSED',)


        for category in self.categories_filter:
            result = []
            _count = 0
            for obj in queryset:
                if _count >= category['limit']:
                    break
                elif self.filter_condition(obj, category):
                    result.append(obj.id)
                    _count += 1
            filtered_list.extend(result)

        return queryset.filter(id__in=filtered_list)
