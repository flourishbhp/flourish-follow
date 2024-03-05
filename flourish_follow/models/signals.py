from django.apps import apps as django_apps
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_constants.constants import YES

from ..models.worklist import WorkList
from .home_visit_models import InPersonLog, InPersonContactAttempt
from .call_models import LogEntry
from .booking import Booking
from .contact import Contact


@receiver(post_save, weak=False, sender=LogEntry,
          dispatch_uid="cal_log_entry_on_post_save")
def cal_log_entry_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        # Update worklist
        try:
            work_list = WorkList.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except WorkList.DoesNotExist:
            pass
        else:
            if 'none_of_the_above' not in instance.phone_num_success and instance.phone_num_success:
                work_list.is_called = True
                work_list.called_datetime = instance.call_datetime
                work_list.user_modified = instance.user_modified
                work_list.save()

        # Create or update a booking
        SubjectLocator = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        if instance.appt == YES:
            try:
                locator = SubjectLocator.objects.get(
                    study_maternal_identifier=instance.study_maternal_identifier)
            except SubjectLocator.DoesNotExist:
                return None
            else:
                try:
                    booking = Booking.objects.get(
                        study_maternal_identifier=instance.study_maternal_identifier)
                except Booking.DoesNotExist:
                    Booking.objects.create(
                        study_maternal_identifier=instance.study_maternal_identifier,
                        first_name=locator.first_name,
                        last_name=locator.last_name,
                        booking_date=instance.appt_date,
                        appt_type=instance.appt_type)
                else:
                    booking.booking_date = instance.appt_date
                    booking.appt_type = instance.appt_type
                    booking.save()

        # Add user to Recruiters group
        try:
            recruiters_group = Group.objects.get(name='Recruiters')
        except Group.DoesNotExist:
            raise ValidationError('Recruiters group must exist.')
        else:
            try:
                user = User.objects.get(username=instance.user_created)
            except User.DoesNotExist:
                raise ValueError(f'The user {instance.user_created}, does not exist.')
            else:
                if not User.objects.filter(username=instance.user_created,
                                           groups__name='Recruiters').exists():
                    recruiters_group.user_set.add(user)


@receiver(post_save, weak=False, sender=WorkList,
          dispatch_uid="worklist_on_post_save")
def worklist_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            InPersonLog.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except InPersonLog.DoesNotExist:
            InPersonLog.objects.create(
                worklist=instance,
                study_maternal_identifier=instance.study_maternal_identifier)

        # Add user to assignable group
        app_config = django_apps.get_app_config('flourish_follow')
        try:
            assignable_users_group = Group.objects.get(name=app_config.assignable_users_group)
        except Group.DoesNotExist:
            raise ValidationError('assignable users group must exist.')
        else:
            try:
                user = User.objects.get(username=instance.user_created)
            except User.DoesNotExist:
                raise ValueError(f'The user {instance.user_created}, does not exist.')
            else:
                if not User.objects.filter(username=instance.user_created,
                                           groups__name=app_config.assignable_users_group).exists():
                    assignable_users_group.user_set.add(user)


@receiver(post_save, weak=False, sender=InPersonContactAttempt,
          dispatch_uid="in_person_contact_attempt_on_post_save")
def in_person_contact_attempt_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            work_list = WorkList.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except WorkList.DoesNotExist:
            pass
        else:
            if 'none_of_the_above' not in instance.successful_location:
                work_list.visited = True
                work_list.user_modified = instance.user_modified
                work_list.save()


@receiver(post_save, weak=False, sender=Contact, dispatch_uid='fu_contact_on_post_save')
def fu_contact_on_post_save(sender, instance, raw, created, **kwargs):
    participant_note_cls = django_apps.get_model('flourish_calendar.participantnote')

    if not raw and created:
        if getattr(instance, 'appt_date', None):
            participant_note_cls.objects.update_or_create(
                subject_identifier=instance.subject_identifier,
                title='Follow Up Schedule',
                description='Enrolling participant from cohort C sec to primary aims.',
                defaults={'date': instance.appt_date, })
