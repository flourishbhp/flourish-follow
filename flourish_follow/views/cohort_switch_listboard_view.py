from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..model_wrappers import CaregiverCohortModelWrapper
from .export_view_mixin import ExportViewMixin
from .cohort_switch_view_mixin import CohortCHEUSwitchViewMixin
from .filters import CohortSwitchListboardFilters


class CohortSwitchListboardView(ExportViewMixin, CohortCHEUSwitchViewMixin,
                                NavbarViewMixin, EdcBaseViewMixin,
                                ListboardFilterViewMixin,
                                SearchFormViewMixin, ListboardView):

    listboard_template = 'cohort_switch_listboard_template'
    listboard_url = 'cohort_switch_listboard_url'

    model = 'flourish_caregiver.cohort'
    listboard_view_filters = CohortSwitchListboardFilters()
    model_wrapper_cls = CaregiverCohortModelWrapper
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'cohort_switch'
    search_form_url = 'cohort_switch_listboard_url'
    listboard_fa_icon = 'fa fa-random'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('subject_identifier'):
            options.update(
                {'subject_identifier': kwargs.get('subject_identifier')})
        return options

    def get_queryset_exclude_options(self, request, *args, **kwargs):
        """ Exclude participant's from a certain cohort, and exposure status
            if the FUs are already full.
        """
        options = super().get_queryset_exclude_options(request, *args, **kwargs)
        extra_options = self.fu_enrolment_limits_exclude
        options.update(extra_options)
        return options

    @property
    def fu_enrolment_limits_exclude(self):
        """ Check if cohort enrolment FU limit has been reached and exclude
            the specific exposure group per cohort from list of FUs available
            for scheduling.
        """
        exclude_status = []
        cohort_limits = {'cohort_b': [('EXPOSED', 200), ('UNEXPOSED', 100)],
                         'cohort_c': [('EXPOSED', 100), ('UNEXPOSED', 200)]}

        filter_options = self.get_queryset_filter_options(
            self.request, *self.args, **self.kwargs)

        cohort_name = filter_options.get('name', None)
        limits = cohort_limits.get(cohort_name, [])

        schedule_names = self.get_fu_schedule_names(cohort_name)
        child_idx = self.subject_schedule_history_cls.objects.exclude(
            subject_identifier__in=self.child_offstudy_pids).filter(
            schedule_name__in=schedule_names).values_list(
                'subject_identifier', flat=True)
        for limit in limits:
            exposure_status, _count = limit
            limit_childidx = self.model_cls.objects.filter(
                subject_identifier__in=child_idx,
                exposure_status=exposure_status).values_list(
                    'subject_identifier', flat=True)
            limit_childidx = set(limit_childidx)
            if len(limit_childidx) >= _count:
                exclude_status.append(exposure_status)
        return {'exposure_status__in': exclude_status}

    @property
    def export_fields(self):
        return ['subject_identifier', 'name', 'exposure_status',
                'child_gender', 'child_bmi', 'child_age',
                'successful_contact', 'has_fu_appts', ]
