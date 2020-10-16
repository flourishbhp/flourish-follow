from edc_call_manager.model_caller import ModelCaller, DAILY
from edc_call_manager.decorators import register
from edc_call_manager.models import Call, Log, LogEntry
from flourish_maternal.models import MaternalLocator

from ..models import WorkList


@register(WorkList)
class WorkListFollowUpModelCaller(ModelCaller):
    call_model = (Call)
    locator_model = (MaternalLocator, 'subject_identifier')
#     consent_model = (SubjectConsent, 'subject_identifier')
    alternative_locator_filter = 'study_maternal_identifier'
    log_entry_model = LogEntry
    log_model = Log
    interval = DAILY
