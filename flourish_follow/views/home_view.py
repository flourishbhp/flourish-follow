from decimal import Decimal
from django_pandas.io import read_frame
import datetime
import random

from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.urls.base import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from flourish_child.models import ChildDataset

from .download_report_mixin import DownloadReportMixin
from ..forms import (
    AssignParticipantForm, ResetAssignmentForm, ReAssignParticipantForm,
    SingleReAssignParticipantForm)
from ..models import FollowExportFile, WorkList


class HomeView(
        EdcBaseViewMixin, NavbarViewMixin,
        DownloadReportMixin, TemplateView, FormView):

    form_class = AssignParticipantForm
    template_name = 'flourish_follow/home.html'
    navbar_name = 'flourish_follow'
    navbar_selected_item = 'assignments'

    def get_success_url(self):
        return reverse('flourish_follow:home_url')

    def create_user_worklist(self, username=None, selected_participants=None):
        """Sets a work list for a user.
        """
        for participant in selected_participants:
            update_values = {
                'assigned': username,
                'date_assigned': timezone.now().date(),
                'user_modified': self.request.user.username}
            WorkList.objects.update_or_create(
                study_maternal_identifier=participant,
                defaults=update_values)

    @property
    def participants_assignments(self):
        """Return participants assignments.
        """
        assignments = WorkList.objects.filter(assigned__isnull=False).values_list(
                'assigned', 'study_maternal_identifier', 'is_called', 'visited')
        return assignments

    @property
    def over_age_limit(self):
        """Return the list of 17 years 9 months children.
        """
        over_age_limit = ChildDataset.objects.filter(
            age_today__gte=Decimal('17.9')).values_list(
                'study_maternal_identifier', flat=True)
        return list(set(over_age_limit))

    @property
    def available_participants(self):
        mashi_participants = WorkList.objects.filter(
            prev_study='Mashi').values_list(
                'study_maternal_identifier', flat=True)
        identifiers = WorkList.objects.filter(
            is_called=False, assigned=None, date_assigned=None).values_list(
                'study_maternal_identifier', flat=True)
        final_list = list(set(identifiers) & set(mashi_participants))
        final_list = list(set(final_list) - set(self.over_age_limit))
        if not final_list:
            final_list = list(set(identifiers) - set(self.over_age_limit))
        return final_list
    
    @property
    def available_td_participants(self):
        td_participants = WorkList.objects.filter(
            prev_study='Tshilo Dikotla').values_list(
                'study_maternal_identifier', flat=True)
        final_td_list = list(set(td_participants) - set(self.over_age_limit))
        return final_td_list

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

    def re_assign_participant_assignments(
            self, username_from=None, username_to=None):
        WorkList.objects.filter(
                assigned=username_from).update(
                    assigned=username_to,
                    date_assigned=timezone.now().date())

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = [['choose', 'choose']]
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('flourish_follow')
        assignable_users_group = app_config.assignable_users_group
        try:
            Group.objects.get(name=assignable_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=assignable_users_group)
        assignable_users = user.objects.filter(
            groups__name=assignable_users_group)
        extra_choices = []
        if app_config.extra_assignee_choices:
            for _, value in app_config.extra_assignee_choices.items():
                extra_choices.append(value[0][0], value[0][1])
        for assignable_user in assignable_users:
            username = assignable_user.username
            if not assignable_user.first_name:
                raise ValidationError(
                    f"The user {username} needs to set their first name.")
            if not assignable_user.last_name:
                raise ValidationError(
                    f"The user {username} needs to set their last name.")
            full_name = (f'{assignable_user.first_name} '
                         f'{assignable_user.last_name}')
            assignable_users_choices.append([username, full_name])
        if extra_choices:
            assignable_users_choices += extra_choices
        return assignable_users_choices

    def form_valid(self, form):
        if form.is_valid():
            selected_participants = []
            username = form.cleaned_data.get('username')
            participants = form.cleaned_data['participants']

            selected_td_participants = self.get_td_participants(participants, username)
            other_participants = participants - selected_td_participants

            if (len(self.available_participants) < other_participants):
                selected_participants = self.available_participants
            else:
                selected_participants = random.sample(
                    self.available_participants, other_participants)
            self.create_user_worklist(
                username=username, selected_participants=selected_participants)
        return super().form_valid(form)

    def get_td_participants(self, participants, username):
        if (len(self.available_td_participants) < participants):
            selected_td_participants = self.available_td_participants 
        else:
            selected_td_participants = random.sample(
                self.available_td_participants, round(participants * 0.7))
        self.create_user_worklist(
                username=username, selected_participants=selected_td_participants)
        return len(selected_td_participants)

    def export(self):
        """Export data.
        """
        qs = WorkList.objects.filter(assigned__isnull=False)
        df = read_frame(qs, fieldnames=[
            'assigned', 'study_maternal_identifier', 'is_called', 'visited'])
        self.download_data(
            description='Participants Assignments',
            start_date=datetime.datetime.now().date(),
            end_date=datetime.datetime.now().date(),
            report_type='participants_assignment',
            df=df)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reset_assignment_form = ResetAssignmentForm()
        re_assign_participant_form = ReAssignParticipantForm()

        # Export Assignments
        if self.request.GET.get('assignments_export') == 'yes':
            self.export()
            msg = (
                f'Participants file generated succesfully. '
                'Go to the download list to download file.')
            messages.add_message(
                self.request, messages.SUCCESS, msg)
        assignments_downloads = FollowExportFile.objects.filter(
            description='Participants Assignments').order_by('uploaded_at')

        # Reset participants
        if self.request.method == 'POST':
            reset_form = ResetAssignmentForm(self.request.POST)
            if reset_form.is_valid():
                username = reset_form.data['username']
                self.reset_participant_assignments(username=username)

        # Re-assign participants
        if self.request.method == 'POST':
            re_assign_form = ReAssignParticipantForm(self.request.POST)
            if re_assign_form.is_valid():
                username_from = re_assign_form.data['username_from']
                username_to = re_assign_form.data['username_to']
                self.re_assign_participant_assignments(
                    username_from=username_from,
                    username_to=username_to)

        # Single participant re-assignment
        if self.request.method == 'POST':
            single_re_assign_form = SingleReAssignParticipantForm(
                self.request.POST)
            if single_re_assign_form.is_valid():
                reassign_name = single_re_assign_form.data['reassign_name']
                username_from = single_re_assign_form.data['username_from']
                study_maternal_identifier = single_re_assign_form.data[
                    'study_maternal_identifier']
                WorkList.objects.filter(
                    assigned=username_from,
                    study_maternal_identifier=study_maternal_identifier).update(
                    assigned=reassign_name,
                    date_assigned=timezone.now().date())

        context.update(
            participants_assignments=self.participants_assignments,
            reset_assignment_form=reset_assignment_form,
            re_assign_participant_form=re_assign_participant_form,
            assign_users=self.assign_users,
            assignments_downloads=assignments_downloads)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
