from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from edc_base.sites import SiteModelFormMixin

from .models import WorkList

USERS = (
    ('nicholas', 'Nicholas'),
    ('sammmuel_kgole', 'Sammuel Kgole'),
)


class WorkListForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = WorkList
        fields = '__all__'


class AssignParticipantForm(forms.Form):

    username = forms.ChoiceField(
        choices=USERS, required=True, label='Username')

    participants = forms.IntegerField(
        required=True, label='Request participants')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
