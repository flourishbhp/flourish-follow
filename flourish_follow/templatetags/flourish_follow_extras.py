from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.inclusion_tag('flourish_follow/buttons/dashboard_button.html')
def dashboard_button(model_wrapper, url_name):
    subject_dashboard_url = settings.DASHBOARD_URL_NAMES.get(url_name)
    return dict(
        subject_dashboard_url=subject_dashboard_url,
        subject_identifier=model_wrapper.subject_identifier)


@register.inclusion_tag('flourish_follow/buttons/caregiver_contact_log.html')
def caregiver_contact_log(model_wrapper):
    title = 'Contact outcomes'

    return dict(
        add_button=model_wrapper.successful_contact,
        contact_obj=model_wrapper.caregiver_contact,
        contact_objects=model_wrapper.caregiver_contacts,
        title=title)
