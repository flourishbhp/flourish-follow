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

from flourish_caregiver.helper_classes import Cohort
from flourish_caregiver.models import CaregiverLocator, MaternalDataset

from ..forms import AssignParticipantForm, ResetAssignmentForm
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
        for participant in selected_participants:
            update_values = {
                'assigned': self.request.user.username,
                'date_assigned': timezone.now().date()}
            WorkList.objects.update_or_create(
                study_maternal_identifier=participant,
                defaults=update_values)


    @property
    def participants_assignments(self):
        """Return participants assignments.
        """
        assignments = WorkList.objects.filter(
            date_assigned=timezone.now().date()).values_list(
                'assigned', 'study_maternal_identifier',)
        return assignments

    @property
    def over_age_limit(self):
        """Return the list of 17 years 9 months children.
        """
        maternal_data = MaternalDataset.objects.all()
        over_age_limit = []
        for maternal in maternal_data:
            age = Cohort().age_at_enrollment(
                child_dob=maternal.delivdt, check_date=timezone.now().date())
            if age >= 17.9:
                over_age_limit.append(maternal.study_maternal_identifier)
        return over_age_limit

    @property
    def available_participants(self):
        locator_identifiers = CaregiverLocator.objects.values_list(
            'study_maternal_identifier', flat=True).distinct()
        called_assigned_identifiers = WorkList.objects.filter(
            Q(is_called=True) | Q(date_assigned=timezone.now().date())).values_list(
                'study_maternal_identifier', flat=True)
        locator_identifiers = list(set(locator_identifiers) - set(self.over_age_limit))
        return list(set(locator_identifiers) - set(called_assigned_identifiers))

    def reset_participant_assignments(self, username=None):
        """Resets all assignments if reset is yes.
        """
        if username == 'all':
            WorkList.objects.filter(
                date_assigned__isnull=False,
                assigned__isnull=False).update(
                    assigned=None, date_assigned=None)
        else:
            WorkList.objects.filter(
                date_assigned__isnull=False,
                assigned=username).update(
                    assigned=None, date_assigned=None)

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
        reset_assignment_form = ResetAssignmentForm()
        if self.request.method == 'POST':
            reset_assignment_form = ResetAssignmentForm(self.request.POST)
            if reset_assignment_form.is_valid():
                username = reset_assignment_form.data['username']
                self.reset_participant_assignments(username=username)
        
        context.update(
            participants_assignments=self.participants_assignments,
            total_assigned=len(self.participants_assignments),
            available_participants=len(self.available_participants),
            total_locators=CaregiverLocator.objects.all().count(),
            successful_calls=WorkList.objects.filter(is_called=True).count(),
            reset_assignment_form=reset_assignment_form)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
