from decimal import Decimal
import random
import re

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls.base import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from edc_dashboard.view_mixins import (
    ListboardFilterViewMixin, SearchFormViewMixin)
from edc_dashboard.views import ListboardView
from flourish_child.models import ChildDataset

from ..forms import ParticipantsNumberForm
from ..model_wrappers import WorkListModelWrapper
from ..models import WorkList
from .filters import ListboardViewFilters
from .worklist_queryset_view_mixin import WorkListQuerysetViewMixin


# from django.apps import apps as django_apps
class ListboardView(NavbarViewMixin, EdcBaseViewMixin,
                    ListboardFilterViewMixin, SearchFormViewMixin,
                    WorkListQuerysetViewMixin,
                    ListboardView, FormView):

    form_class = ParticipantsNumberForm
    listboard_template = 'flourish_follow_listboard_template'
    listboard_url = 'flourish_follow_listboard_url'
    listboard_panel_style = 'info'
    listboard_fa_icon = "fa-user-plus"

    model = 'flourish_follow.worklist'
    listboard_view_filters = ListboardViewFilters()
    model_wrapper_cls = WorkListModelWrapper
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'worklist'
    ordering = '-modified'
    paginate_by = 10
    search_form_url = 'flourish_follow_listboard_url'

    def get_success_url(self):
        return reverse('flourish_follow:flourish_follow_listboard_url')

    def create_user_worklist(self, selected_participants=None):
        """Sets a work list for a user.
        """
        for participant in selected_participants:
            update_values = {
                'assigned': self.request.user.username,
                'date_assigned': timezone.now().date()}
            WorkList.objects.update_or_create(
                study_maternal_identifier=participant,
                defaults=update_values)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if form.is_valid():
            participants = form.cleaned_data['participants']

            self.get_participants(participants, ratio=0.5, prev_study='Tshilo Dikotla')

            self.get_participants(participants, ratio=0.5, prev_study='Mma Bana')

        return super().form_valid(form)

    def get_participants(self, participants, ratio=None, prev_study=None):

        available_participants = self.available_participants(prev_study=prev_study)

        if not available_participants:
            available_participants = self.available_participants()

        if (len(available_participants) < participants):
            selected_participants = self.available_participants(prev_study=prev_study)
        else:
            if ratio:
                selected_participants = random.sample(
                    available_participants, round(participants * ratio))
            else:
                selected_participants = random.sample(
                    available_participants, participants)

        self.create_user_worklist(selected_participants=selected_participants)
        return len(selected_participants)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('subject_identifier'):
            options.update(
                {'subject_identifier': kwargs.get('subject_identifier')})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q

    @property
    def over_age_limit(self):
        """Return the list of 17 years 9 months children.
        """
        over_age_limit = ChildDataset.objects.filter(
            age_today__gte=Decimal('17.9')).values_list(
                'study_maternal_identifier', flat=True)
        return list(set(over_age_limit))

    def available_participants(self, prev_study=None):

        if prev_study:
            identifiers = WorkList.objects.filter(
                prev_study=prev_study, consented=False,
                is_called=False, assigned=None, date_assigned=None).values_list(
                    'study_maternal_identifier', flat=True)
        else:
            identifiers = WorkList.objects.filter(
                is_called=False,
                assigned=None,
                date_assigned=None,
                consented=False).values_list(
                    'study_maternal_identifier', flat=True)

        final_list = list(set(identifiers) - set(self.over_age_limit))

        return final_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            total_results=self.get_queryset().count(),
            called_subject=WorkList.objects.filter(is_called=True).count(),
            visited_subjects=WorkList.objects.filter(visited=True).count(),
            total_available=len(self.available_participants()),
        )
        return context
