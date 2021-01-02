from django.db import models

from edc_base.model_mixins import BaseUuidModel

from edc_call_manager.model_mixins import (
    CallModelMixin, LogModelMixin, LogEntryModelMixin)


class Call(CallModelMixin, BaseUuidModel):

    class Meta(CallModelMixin.Meta):
        app_label = 'flourish_follow'


class Log(LogModelMixin, BaseUuidModel):

    call = models.ForeignKey(Call, on_delete=models.PROTECT)


    class Meta(LogModelMixin.Meta):
        app_label = 'flourish_follow'


class LogEntry(LogEntryModelMixin, BaseUuidModel):

    log = models.ForeignKey(Log, on_delete=models.PROTECT)

    class Meta(LogEntryModelMixin.Meta):
        app_label = 'flourish_follow'
