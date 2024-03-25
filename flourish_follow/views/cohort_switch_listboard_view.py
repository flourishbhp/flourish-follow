from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..model_wrappers import CaregiverCohortModelWrapper
from .cohort_switch_view_mixin import CohortCHEUSwitchViewMixin
from .filters import CohortSwitchListboardFilters


class CohortSwitchListboardView(CohortCHEUSwitchViewMixin, NavbarViewMixin,
                                EdcBaseViewMixin, ListboardFilterViewMixin,
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
