from django import forms
from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from edc_form_validators import FormValidatorMixin

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from edc_base.sites import SiteModelFormMixin

from .models import WorkList, LogEntry


class WorkListForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = WorkList
        fields = '__all__'


class AssignParticipantForm(forms.Form):

    username = forms.ChoiceField(
        required=True, label='Username',
        widget=forms.Select())

    participants = forms.IntegerField(
        required=True, label='Request participants')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.assign_users
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'assign_participant'
        self.helper.form_action = 'flourish_follow:home_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'participants',  # field1 will appear first in HTML
            Submit('submit', u'Assign', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = ()
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('edc_data_manager')
        assignable_users_group = app_config.assignable_users_group
        try:
            Group.objects.get(name=assignable_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=assignable_users_group)
        assignable_users = user.objects.filter(
            groups__name=assignable_users_group)
        extra_choices = ()
        if app_config.extra_assignee_choices:
            for _, value in app_config.extra_assignee_choices.items():
                extra_choices += (value[0],)
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
            assignable_users_choices += ((username, full_name),)
        if extra_choices:
            assignable_users_choices += extra_choices
        return assignable_users_choices


class ParticipantsNumberForm(forms.Form):

    participants = forms.IntegerField(
        required=True, label='Request participants')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'select_participant'
        self.helper.form_action = 'flourish_follow:flourish_follow_listboard_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'participants',  # field1 will appear first in HTML
            Submit('submit', u'Randomize', css_class="btn btn-sm btn-default"),
        )


class LogEntryForm(
        SiteModelFormMixin, FormValidatorMixin,
        forms.ModelForm):

    study_maternal_identifier = forms.CharField(
        label='Study maternal Subject Identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = LogEntry
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = self.update_choices_vars(self.custom_choices)
        self.fields['phone_num_type'] = forms.MultipleChoiceField(
            label='Which phone number(s) was used for contact?',
            widget=forms.CheckboxSelectMultiple, choices=choices)
        self.fields['phone_num_success'] = forms.MultipleChoiceField(
            label='Which number(s) were you successful in reaching?',
            widget=forms.CheckboxSelectMultiple, choices=choices)

    def update_choices_vars(self, choices_list=[]):
        new_choices = []
        for choices in choices_list:
            choices[0] = choices[0].removesuffix('_fail')
            new_choices.append(tuple(choices))
        return new_choices

