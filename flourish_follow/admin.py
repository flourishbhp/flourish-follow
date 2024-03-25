from django.apps import apps as django_apps
from django.contrib import admin
from django.conf import settings

from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch

from edc_model_admin.model_admin_next_url_redirect_mixin import ModelAdminNextUrlRedirectError
from edc_constants.constants import NOT_APPLICABLE
from edc_base.sites.admin import ModelAdminSiteMixin
from edc_model_admin import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminAuditFieldsMixin,
    ModelAdminReadOnlyMixin, ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin)
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin import ModelAdminBasicMixin
from edc_model_admin.changelist_buttons import ModelAdminChangelistModelButtonMixin

from .exportaction_mixin import ExportActionMixin
from .admin_site import flourish_follow_admin
from .forms import (
    BookingForm, ContactForm, WorkListForm, LogEntryForm, InPersonContactAttemptForm)
from .models import (
    Booking, Call, Contact, WorkList, Log, LogEntry, InPersonContactAttempt,
    InPersonLog)


class ModelAdminMixin(ModelAdminNextUrlRedirectMixin,
                      ModelAdminFormInstructionsMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                      ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
                      ModelAdminInstitutionMixin,
                      ModelAdminRedirectOnDeleteMixin,
                      ModelAdminSiteMixin,
                      ExportActionMixin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'


@admin.register(Contact, site=flourish_follow_admin)
class ContactAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = ContactForm

    search_fields = ('subject_identifier', )

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'report_datetime',
                'contact_type',
                'contact_datetime',
                'contact_success',
                'appt_scheduled',
                'appt_date',
                'final_contact',
            )},
        ), audit_fieldset_tuple)

    list_display = ['subject_identifier', 'contact_type',
                    'contact_datetime']

    list_filter = ['contact_type', 'contact_success', 'final_contact']

    radio_fields = {
        'contact_type': admin.VERTICAL,
        'contact_success': admin.VERTICAL,
        'appt_scheduled': admin.VERTICAL,
        'final_contact': admin.VERTICAL, }

    def get_next_redirect_url(self, request=None):
        url_name = request.GET.dict().get(
            self.next_querystring_attr).split(',')[0]
        options = self.get_next_options(request=request)
        cohort_name = options.pop('cohort_name', None)
        try:
            redirect_url = reverse(url_name, kwargs=options)
        except NoReverseMatch as e:
            msg = f'{e}. Got url_name={url_name}, kwargs={options}.'
            try:
                redirect_url = reverse(url_name)
            except NoReverseMatch:
                raise ModelAdminNextUrlRedirectError(msg)
        return f'{redirect_url}?f={cohort_name}' if cohort_name and 'sec' not in cohort_name else redirect_url

@admin.register(Booking, site=flourish_follow_admin)
class BookingAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = BookingForm

    fieldsets = (
        (None, {
            'fields': (
                'study_maternal_identifier',
                'first_name',
                'last_name',
                'booking_date',
                'appt_type',)}),
        audit_fieldset_tuple)

    list_display = ('first_name', 'last_name',)


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

    list_display = ('subject_identifier', 'study_maternal_identifier', 'prev_study', 'is_called')


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

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
                       'phone_num_success',)
        }),

        ('Subject Cell & Telephones', {
            'fields': ('cell_contact_fail',
                       'alt_cell_contact_fail',
                       'tel_contact_fail',
                       'alt_tel_contact_fail',)
        }),
        ('Subject Work Contact', {
            'fields': ('work_contact_fail',)
        }),
        ('Indirect Contact Cell & Telephone', {
            'fields': ('cell_alt_contact_fail',
                       'tel_alt_contact_fail',)
        }),
        ('Caretaker Cell & Telephone', {
            'fields': ('cell_resp_person_fail',
                       'tel_resp_person_fail')
        }),
        ('Schedule Appointment With Participant', {
           'fields': ('appt',
                      'appt_type',
                      'other_appt_type',
                      'appt_reason_unwilling',
                      'appt_reason_unwilling_other',
                      'appt_date',
                      'appt_grading',
                      'appt_location',
                      'appt_location_other',
                      'may_call',
                      'home_visit',
                      'home_visit_other',
                      'final_contact',
                      )
        }), audit_fieldset_tuple)

    radio_fields = {'appt': admin.VERTICAL,
                    'appt_type': admin.VERTICAL,
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
                    'tel_resp_person_fail': admin.VERTICAL,
                    'home_visit': admin.VERTICAL,
                    'final_contact': admin.VERTICAL,
                    }

    filter_horizontal = ('appt_reason_unwilling', )

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
                form.base_fields[field].label = f'{idx +1}. Why was the contact to {custom_value} unsuccessful?'
        form.custom_choices = self.phone_choices(study_maternal_identifier)
        return form

    def redirect_url(self, request, obj, post_url_continue=None):
        redirect_url = super().redirect_url(
            request, obj, post_url_continue=post_url_continue)
        if ('none_of_the_above' not in obj.phone_num_success
                and obj.home_visit == NOT_APPLICABLE):
            if request.GET.dict().get('next'):
                url_name = settings.DASHBOARD_URL_NAMES.get(
                    'maternal_dataset_listboard_url')
            options = {'study_maternal_identifier': request.GET.dict().get('study_maternal_identifier')}
            try:
                redirect_url = reverse(url_name, kwargs=options)
            except NoReverseMatch as e:
                raise ModelAdminNextUrlRedirectError(
                    f'{e}. Got url_name={url_name}, kwargs={options}.')
        return redirect_url

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
                    field_name = field_attr.replace('_', ' ')
                    value = f'{value} {field_name.title()}'
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

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['log'].queryset = \
            Log.objects.filter(id=request.GET.get('log'))
        return super(LogEntryAdmin, self).render_change_form(
            request, context, *args, **kwargs)


@admin.register(InPersonContactAttempt, site=flourish_follow_admin)
class InPersonContactAttemptAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = InPersonContactAttemptForm

    search_fields = ['study_maternal_identifier']

    fieldsets = (
        (None, {
            'fields': ('in_person_log',
                       'study_maternal_identifier',
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

        if obj:
            study_maternal_identifier = getattr(obj, 'study_maternal_identifier', '')
        else:
            study_maternal_identifier = request.GET.get('study_maternal_identifier')

        fields = self.get_all_fields(form)

        for idx, field in enumerate(fields):
            custom_value = self.custom_field_label(study_maternal_identifier,
                                                   field)

            if custom_value:
                form.base_fields[field].label = f'{idx +1}. Why was the in-person visit to {custom_value} unsuccessful?'
        form.custom_choices = self.home_visit_choices(study_maternal_identifier)
        return form

    def home_visit_choices(self, study_identifier):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        field_attrs = [
            'physical_address',
            'subject_work_place',
            'indirect_contact_physical_address']

        try:
            locator_obj = caregiver_locator_cls.objects.get(
                study_maternal_identifier=study_identifier)
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            home_visit_choices = ()
            for field_attr in field_attrs:
                value = getattr(locator_obj, field_attr)
                if value:
                    home_visit_choices += ((field_attr, value),)
            return home_visit_choices

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

    def redirect_url(self, request, obj, post_url_continue=None):
        redirect_url = super().redirect_url(
            request, obj, post_url_continue=post_url_continue)
        if 'none_of_the_above' not in obj.successful_location:
            if request.GET.dict().get('next'):
                url_name = settings.DASHBOARD_URL_NAMES.get(
                    'maternal_dataset_listboard_url')
            options = {'study_maternal_identifier': request.GET.dict().get('study_maternal_identifier')}
            try:
                redirect_url = reverse(url_name, kwargs=options)
            except NoReverseMatch as e:
                raise ModelAdminNextUrlRedirectError(
                    f'{e}. Got url_name={url_name}, kwargs={options}.')
        return redirect_url

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['in_person_log'].queryset = \
            InPersonLog.objects.filter(id=request.GET.get('in_person_log'))
        return super().render_change_form(request, context, *args, **kwargs)
