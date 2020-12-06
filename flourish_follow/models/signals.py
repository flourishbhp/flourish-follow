from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_call_manager.models import LogEntry
from flourish_caregiver.models import MaternalVisit

from ..models.worklist import WorkList


@receiver(post_save, weak=False, sender=LogEntry,
          dispatch_uid="cal_log_entry_on_post_save")
def cal_log_entry_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            work_list = WorkList.objects.get(
                subject_identifier=instance.log.call.subject_identifier)
        except WorkList.DoesNotExist:
            pass
        else:
            work_list.is_called = True
            work_list.called_datetime = instance.call_datetime
            work_list.save()


@receiver(post_save, weak=False, sender=MaternalVisit,
          dispatch_uid="materal_visit_on_post_save")
def maternal_visit_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            work_list = WorkList.objects.get(
                subject_identifier=instance.subject_identifier)
        except WorkList.DoesNotExist:
            pass
        else:
            work_list.visited = True
            work_list.save()
