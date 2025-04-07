from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..helper_classes.cohort_limits import CohortLimitsMixin
from ..model_wrappers import CaregiverCohortModelWrapper
from .export_view_mixin import ExportViewMixin
from .cohort_switch_view_mixin import CohortCHEUSwitchViewMixin
from .filters import CohortSwitchListboardFilters


class CohortSwitchListboardView(ExportViewMixin, CohortLimitsMixin,
                                CohortCHEUSwitchViewMixin,
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
        neuro_crf_counts = {}
        cohort_b_heu, cohort_b_huu = self.cohort_b_current_counts(
            per_crf_counts=neuro_crf_counts)
        neuro_breakdown = self.get_neuro_crf_breakdown(neuro_crf_counts)
        cohort_c_heu, cohort_c_huu = self.cohort_c_current_counts()

        context.update(
            {'cohort_b_heu': cohort_b_heu,
             'cohort_b_huu': cohort_b_huu,
             'neuro_breakdown': neuro_breakdown,
             'cohort_c_heu': cohort_c_heu,
             'cohort_c_huu': cohort_c_huu})
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

        filter_options = self.get_queryset_filter_options(
            self.request, *self.args, **self.kwargs)

        cohort_name = filter_options.get('name', None)
        prev_study = self.request.GET.get('f', None)
        if cohort_name:
            self.check_limits_reached(cohort_name, exclude_status)
        elif prev_study == 'pre_flourish':
            # Cohort B HUU is already being excluded. All PF participants
            # Are HUU.
            cohort_names = ['cohort_c', ]
            for cohort_name in cohort_names:
                self.check_limits_reached(cohort_name, exclude_status)

        return {'exposure_status__in': exclude_status}

    @property
    def export_fields(self):
        return ['subject_identifier', 'name', 'exposure_status',
                'child_gender', 'child_bmi', 'child_age',
                'successful_contact', 'has_fu_appts', ]
