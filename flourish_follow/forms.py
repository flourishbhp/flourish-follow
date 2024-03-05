from django import forms
from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from edc_base.sites import SiteModelFormMixin
from edc_form_validators import FormValidatorMixin


from .models import Booking, WorkList, LogEntry, InPersonContactAttempt, Contact
from .form_validations import (FUContactFormValidator, LogEntryFormValidator,
                               HomeVisitFormValidator)


class WorkListForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = WorkList
        fields = '__all__'


class BookingForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = Booking
        fields = '__all__'


class ContactForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = FUContactFormValidator

    subject_identifier = forms.CharField(
        label='Subject Identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Contact
        fields = '__all__'
        

class AppointmentRegistrationForm(forms.Form):

    first_name = forms.CharField(
            required=True, label='Firstname')

    middle_name = forms.CharField(
            required=False, label='Middlename')

    last_name = forms.CharField(
            required=True, label='Lastname')

    subject_cell = forms.IntegerField(
        required=True, label='Cell Number')

    booking_date = forms.DateField(
        required=True, label='Booking date',
        widget=forms.TextInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'appointment_registration'
        self.helper.form_action = 'flourish_follow:flourish_follow_book_listboard_url'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'first_name',
            'middle_name',
            'last_name',
            'subject_cell',
            'booking_date',
            Submit('submit', u'Book participant', css_class="btn btn-sm btn-default")
        )



class AppointmentsWindowForm(forms.Form):

    start_date = forms.DateField(
        required=False, label='Start date',
        widget=forms.TextInput(attrs={'type': 'date'}))
    
    end_date = forms.DateField(
        required=False, label='End date',
        widget=forms.TextInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'appointment'
        self.helper.form_action = 'flourish_follow:flourish_follow_appt_listboard_url'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'start_date',
            'end_date',
            Submit('submit', u'filter report', css_class="btn btn-sm btn-default")
        )
        


class SingleReAssignParticipantForm(forms.Form):

    reassign_name = forms.CharField(
        required=True, label='Assign to')
    username_from = forms.CharField(
        required=True, label='Username from')
    study_maternal_identifier = forms.CharField(
        required=True, label='study maternal identifier')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'singlereassign_participant'
        self.helper.form_action = 'flourish_follow:home_url'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            'reassign_name',
            'username_from',
            'study_maternal_identifier',
            Submit('submit', u'single re-Assign', css_class="btn btn-sm btn-default"),
        )


class ReAssignParticipantForm(forms.Form):

    username_from = forms.ChoiceField(
        required=True, label='Username from',
        widget=forms.Select())

    username_to = forms.ChoiceField(
        required=True, label='Username to',
        widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username_from'].choices = self.assign_users
        self.fields['username_to'].choices = self.assign_users
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'reassign_participant'
        self.helper.form_action = 'flourish_follow:home_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username_from',
            'username_to',
            Submit('submit', u'Re-Assign', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = (('-----', '-----'),)
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('flourish_follow')
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


class AssignParticipantForm(forms.Form):

    username = forms.ChoiceField(
        required=True, label='Username',
        widget=forms.Select())

    participants = forms.IntegerField(
        required=True, label='participants #')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.assign_users
        self.fields['participants'].widget.attrs.update(style='max-width: 7em')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'assign_participant'
        self.helper.form_action = 'flourish_follow:home_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'participants',
            Submit('submit', u'Assign', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = ()
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('flourish_follow')
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


class ResetAssignmentForm(forms.Form):

    username = forms.ChoiceField(
        required=True, label='Username',
        widget=forms.Select())

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
            Submit('submit', u'Reset', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = (('all', 'All'),)
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('flourish_follow')
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

    form_validator_cls = LogEntryFormValidator

    study_maternal_identifier = forms.CharField(
        label='Study maternal Subject Identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    prev_study = forms.CharField(
        label=' Previous Study Name',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    phone_num_type = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label='Which phone number(s) was used for contact?')

    phone_num_success = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label='Which number(s) were you successful in reaching?')

    class Meta:
        model = LogEntry
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = self.custom_choices
        self.fields['phone_num_type'].choices = choices
        self.fields['phone_num_success'].choices = choices + (('none_of_the_above', 'None of the above'),)


class InPersonContactAttemptForm(
        SiteModelFormMixin, FormValidatorMixin,
        forms.ModelForm):

    form_validator_cls = HomeVisitFormValidator

    study_maternal_identifier = forms.CharField(
        label='Study maternal Subject Identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    prev_study = forms.CharField(
        label=' Previous Study Name',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    contact_location = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label='Which location was used for contact?')

    successful_location = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label='Which location(s) were successful?')

    class Meta:
        model = InPersonContactAttempt
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = self.custom_choices
        if choices:
            self.fields['contact_location'].choices = choices
            self.fields['successful_location'].choices = choices + (
                ('none_of_the_above', 'None of the above'),)
