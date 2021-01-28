from django.apps import apps as django_apps
from django.contrib import admin

from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_base.sites.admin import ModelAdminSiteMixin
from edc_model_admin import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminAuditFieldsMixin,
    ModelAdminReadOnlyMixin, ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin)
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin import ModelAdminBasicMixin
from edc_call_manager.constants import NEW_CALL, OPEN_CALL
from edc_model_admin.changelist_buttons import ModelAdminChangelistModelButtonMixin

from .admin_site import flourish_follow_admin
from .forms import WorkListForm, LogEntryForm, InPersonContactAttemptForm
from .models import Call, WorkList, Log, LogEntry, InPersonContactAttempt


class ModelAdminMixin(ModelAdminNextUrlRedirectMixin,
                      ModelAdminFormInstructionsMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                      ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
                      ModelAdminInstitutionMixin,
                      ModelAdminRedirectOnDeleteMixin,
                      ModelAdminSiteMixin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'


@admin.register(WorkList, site=flourish_follow_admin)
class WorkListAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = WorkListForm

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'study_maternal_identifier',
                'report_datetime',
                'prev_study',
                'is_called',
                'called_datetime',
                'visited',)}),
        audit_fieldset_tuple)

    instructions = ['Complete this form once per day.']


class ModelAdminCallMixin(ModelAdminChangelistModelButtonMixin, ModelAdminBasicMixin):

    date_hierarchy = 'modified'

    mixin_fields = (
        'call_attempts',
        'call_status',
        'call_outcome',
    )

    mixin_radio_fields = {'call_status': admin.VERTICAL}

    list_display_pos = None
    mixin_list_display = (
        'subject_identifier',
        'call_attempts',
        'call_outcome',
        'scheduled',
        'label',
        'first_name',
        'initials',
        'user_created',
    )

    mixin_list_filter = (
        'call_status',
        'call_attempts',
        'modified',
        'hostname_created',
        'user_created',
    )

    mixin_readonly_fields = (
        'call_attempts',
    )

    mixin_search_fields = ('subject_identifier', 'initials', 'label')



@admin.register(Call, site=flourish_follow_admin)
class CallAdmin(ModelAdminMixin, ModelAdminCallMixin, admin.ModelAdmin):
    pass


@admin.register(Log, site=flourish_follow_admin)
class LogAdmin(ModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(LogEntry, site=flourish_follow_admin)
class LogEntryAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = LogEntryForm

    search_fields = ['study_maternal_identifier']

    fieldsets = (
        (None, {
            'fields': ('log',
                        'study_maternal_identifier',
                       'prev_study',
                       'call_datetime',
                       'phone_num_type',
                       'phone_num_success',
                       'cell_contact_fail',
                       'alt_cell_contact_fail',
                       'tel_contact_fail',
                       'alt_tel_contact_fail',
                       'work_contact_fail',
                       'cell_alt_contact_fail',
                       'tel_alt_contact_fail',
                       'cell_resp_person_fail',
                       'tel_resp_person_fail',
                       'survival_status',
                       'appt',
                       'appt_reason_unwilling',
                       'appt_reason_unwilling_other',
                       'appt_date',
                       'appt_grading',
                       'appt_location',
                       'appt_location_other',
                       'may_call')},
         ),
        audit_fieldset_tuple
    )

    radio_fields = {'survival_status': admin.VERTICAL,
                    'appt': admin.VERTICAL,
                    'appt_reason_unwilling': admin.VERTICAL,
                    'appt_grading': admin.VERTICAL,
                    'appt_location': admin.VERTICAL,
                    'may_call': admin.VERTICAL,
                    'cell_contact_fail': admin.VERTICAL,
                    'alt_cell_contact_fail': admin.VERTICAL,
                    'tel_contact_fail': admin.VERTICAL,
                    'alt_tel_contact_fail': admin.VERTICAL,
                    'work_contact_fail': admin.VERTICAL,
                    'cell_alt_contact_fail': admin.VERTICAL,
                    'tel_alt_contact_fail': admin.VERTICAL,
                    'cell_resp_person_fail': admin.VERTICAL,
                    'tel_resp_person_fail': admin.VERTICAL}

    list_display = (
        'study_maternal_identifier', 'prev_study', 'call_datetime', )

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)

        if obj:
            study_maternal_identifier = getattr(obj, 'study_maternal_identifier', '')
        else:
            study_maternal_identifier = request.GET.get('study_maternal_identifier')

        fields = self.get_all_fields(form)

        for idx, field in enumerate(fields):
            custom_value = self.custom_field_label(study_maternal_identifier, field)

            if custom_value:
                form.base_fields[field].label = f'{idx + 1}. Why was the contact to {custom_value} unsuccessful?'
        form.custom_choices = self.phone_choices(study_maternal_identifier)
        return form

    def phone_choices(self, study_identifier):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        field_attrs = [
            'subject_cell',
            'subject_cell_alt',
            'subject_phone',
            'subject_phone_alt',
            'subject_work_phone',
            'indirect_contact_cell',
            'indirect_contact_phone',
            'caretaker_cell',
            'caretaker_tel']

        try:
            locator_obj = caregiver_locator_cls.objects.get(
                study_maternal_identifier=study_identifier)
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            phone_choices = ()
            for field_attr in field_attrs:
                value = getattr(locator_obj, field_attr)
                if value:
                    phone_choices += ((field_attr, value),)
            return phone_choices

    def custom_field_label(self, study_identifier, field):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        fields_dict = {
            'cell_contact_fail': 'subject_cell',
            'alt_cell_contact_fail': 'subject_cell_alt',
            'tel_contact_fail': 'subject_phone',
            'alt_tel_contact_fail': 'subject_phone_alt',
            'work_contact_fail': 'subject_work_phone',
            'cell_alt_contact_fail': 'indirect_contact_cell',
            'tel_alt_contact_fail': 'indirect_contact_phone',
            'cell_resp_person_fail': 'caretaker_cell',
            'tel_resp_person_fail': 'caretaker_tel'}

        try:
            locator_obj = caregiver_locator_cls.objects.get(
                study_maternal_identifier=study_identifier)
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            attr_name = fields_dict.get(field, None)
            if attr_name:
                return getattr(locator_obj, attr_name, '')

    def get_all_fields(self, instance):
        """"
        Return names of all available fields from given Form instance.

        :arg instance: Form instance
        :returns list of field names
        :rtype: list
        """

        fields = list(instance.base_fields)

        for field in list(instance.declared_fields):
            if field not in fields:
                fields.append(field)
        return fields


@admin.register(InPersonContactAttempt, site=flourish_follow_admin)
class InPersonContactAttemptAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = InPersonContactAttemptForm

    search_fields = ['study_maternal_identifier']

    fieldsets = (
        (None, {
            'fields': ('study_maternal_identifier',
                       'prev_study',
                       'contact_date',
                       'contact_location',
                       'successful_location',
                       'phy_addr_unsuc',
                       'phy_addr_unsuc_other',
                       'workplace_unsuc',
                       'workplace_unsuc_other',
                       'contact_person_unsuc',
                       'contact_person_unsuc_other', )},
         ),
        audit_fieldset_tuple
    )

    radio_fields = {'phy_addr_unsuc': admin.VERTICAL,
                    'workplace_unsuc': admin.VERTICAL,
                    'contact_person_unsuc': admin.VERTICAL}

    list_display = (
        'study_maternal_identifier', 'prev_study', 'contact_date', )

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)

        study_maternal_identifier = kwargs.get('study_maternal_identifier', '')

        fields = self.get_all_fields(form)

        for field in fields:
            custom_value = self.custom_field_label(study_maternal_identifier,
                                                   field)

            if custom_value:
                form.base_fields[
                    field].label = f'Why was the in-person visit to {custom_value} unsuccessful?'

        return form

    def custom_field_label(self, study_identifier, field):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        fields_dict = {
            'phy_addr_unsuc': 'physical_address',
            'workplace_unsuc': 'subject_work_place',
            'contact_person_unsuc': 'indirect_contact_physical_address'}

        try:
            locator_obj = caregiver_locator_cls.objects.get(
                study_maternal_identifier=study_identifier)
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            attr_name = fields_dict.get(field, None)
            if attr_name:
                return getattr(locator_obj, attr_name, '')

    def get_all_fields(self, instance):
        """"
        Return names of all available fields from given Form instance.
        """

        fields = list(instance.base_fields)

        for field in list(instance.declared_fields):
            if field not in fields:
                fields.append(field)
        return fields
