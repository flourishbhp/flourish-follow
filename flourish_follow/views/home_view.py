import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls.base import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from flourish_caregiver.models import CaregiverLocator

from ..forms import AssignParticipantForm
from ..models import WorkList


class HomeView(
        EdcBaseViewMixin, NavbarViewMixin,
        TemplateView, FormView):

    form_class = AssignParticipantForm
    template_name = 'flourish_follow/home.html'
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'flourish_follow'

    def get_success_url(self):
        return reverse('flourish_follow:home_url')

    def create_user_worklist(self, username=None, selected_participants=None):
        """Sets a work list for a user.
        """
        for selected_participant in selected_participants:
            try:
                work_list = WorkList.objects.get(
                    study_maternal_identifier=selected_participant)
            except WorkList.DoesNotExist:
                WorkList.objects.create(
                    study_maternal_identifier=selected_participant,
                    assigned=username,
                    date_assigned=timezone.now().date())
            else:
                work_list.assigned = username
                work_list.date_assigned = timezone.now().date()
                work_list.save()

    @property
    def participants_assignments(self):
        """Return participants assignments.
        """
        assignments = WorkList.objects.filter(
            date_assigned=timezone.now().date()).values_list(
                'study_maternal_identifier', flat=True)
        return assignments

    @property
    def available_participants(self):
        locator_identifiers = CaregiverLocator.objects.values_list(
            'study_maternal_identifier', flat=True)
        called_assigned_identifiers = WorkList.objects.filter(
            Q(is_called=True) | Q(date_assigned=timezone.now().date())).values_list(
                'study_maternal_identifier', flat=True) 
        return list(set(locator_identifiers) - set(called_assigned_identifiers))

    def reset_participant_assignments(self, reset=None):
        """Resets all assignments if reset is yes.
        """
        if reset == 'yes':
            for obj in WorkList.objects.filter(
                    date_assigned__isnull=False, assigned__isnull=False):
                obj.assigned = None
                obj.date_assigned = None
                obj.save()

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if form.is_valid():
            selected_participants = []
            username = form.cleaned_data['username']
            participants = form.cleaned_data['participants']
            if len(self.available_participants) < participants:
                selected_participants = self.available_participants
            else:
                selected_participants = random.sample(
                    self.available_participants, participants)
            self.create_user_worklist(
                username=username, selected_participants=selected_participants)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reset_assginments = self.request.GET.get('reset')
        if reset_assginments:
            self.reset_participant_assignments(reset=reset_assginments)
        context.update(
            participants_assignments=self.participants_assignments,
            total_assigned=len(self.participants_assignments),
            available_participants=len(self.available_participants),
            total_locators=CaregiverLocator.objects.all().count())
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
