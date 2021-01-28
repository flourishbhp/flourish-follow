from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models.worklist import WorkList
from .home_visit_models import InPersonLog
from .call_models import LogEntry


@receiver(post_save, weak=False, sender=LogEntry,
          dispatch_uid="cal_log_entry_on_post_save")
def cal_log_entry_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            work_list = WorkList.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except WorkList.DoesNotExist:
            pass
        else:
            if not 'none_of_the_above' in instance.phone_num_success:
                work_list.is_called = True
                work_list.called_datetime = instance.call_datetime
                work_list.save()


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


# @receiver(post_save, weak=False, sender=MaternalVisit,
#           dispatch_uid="materal_visit_on_post_save")
# def maternal_visit_on_post_save(sender, instance, using, raw, **kwargs):
#     if not raw:
#         try:
#             work_list = WorkList.objects.get(
#                 subject_identifier=instance.subject_identifier)
#         except WorkList.DoesNotExist:
#             pass
#         else:
#             work_list.visited = True
#             work_list.save()
