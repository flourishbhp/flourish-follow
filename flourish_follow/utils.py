from django.apps import apps as django_apps
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from .helper_classes.cohort_limits import CohortLimitsMixin
from django.core.mail.message import EmailMultiAlternatives


class FollowUtils:
    caregiver_offstudy_model = 'flourish_prn.caregiveroffstudy'

    @property
    def caregiver_offstudy_model_cls(self):
        return django_apps.get_model(self.caregiver_offstudy_model)

    def caregivers_offstudy(self):
        pids = self.caregiver_offstudy_model_cls.objects.values_list(
            'subject_identifier', flat=True)
        return pids


follow_utils = FollowUtils()


def send_daily_cohort_limit_updates():
    limits_cls = CohortLimitsMixin()

    subject = 'Cohort Limits Update'
    message = ''

    receipients = User.objects.filter(
        groups__name='Daily Email Updates').values_list(
            'email', flat=True)

    neuro_heu, neuro_huu = limits_cls.cohort_b_current_counts()
    cardio_heu, cardio_huu = limits_cls.cohort_c_current_counts()

    if neuro_heu >= 185 and neuro_heu <= 200:
        message += f'<li> Neurobehavioral HEU: {neuro_heu}</li>'
    if neuro_huu >= 85 and neuro_huu <= 100:
        message += f'<li> Neurobehavioral HUU: {neuro_huu}</li>'
    if cardio_heu >= 85 and cardio_heu <= 100:
        message += f'<li> Cohort C HEU: {cardio_heu}</li>'
    if cardio_huu >= 185 and cardio_huu <= 200:
        message += f'<li> Cohort C HUU: {cardio_huu}</li>'

    if message:
        _message = (
            '<html>'
                '<body>'
                    'Good day, all <br><br>'
                    'Please find below the current count'
                    ' for each cohort FUs/Assessments:'
                    f'<ol> {message} </ol>'
                '</body>'
            '</html>')

        msg = EmailMultiAlternatives(
            subject, '', settings.EMAIL_HOST_USER, receipients)
        msg.attach_alternative(_message, "text/html")
        msg.send()
