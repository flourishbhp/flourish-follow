from django import forms

from edc_base.sites import SiteModelFormMixin
from edc_form_validators import FormValidatorMixin

from .models import WorkList


class WorkListForm(SiteModelFormMixin, FormValidatorMixin,
                           forms.ModelForm):

    class Meta:
        model = WorkList
        fields = '__all__'