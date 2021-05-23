from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models.worklist import WorkList
from .home_visit_models import InPersonLog, InPersonContactAttempt
from .call_models import LogEntry


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
                work_list.user_modified=instance.user_modified
                work_list.save()
        
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
                work_list.user_modified=instance.user_modified
                work_list.save()
