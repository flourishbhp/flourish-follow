from edc_call_manager.model_caller import ModelCaller, DAILY
from edc_call_manager.decorators import register

from flourish_caregiver.models import CaregiverLocator

from ..models import Call, Log, LogEntry

from ..models import WorkList


@register(WorkList)
class WorkListFollowUpModelCaller(ModelCaller):
    call_model = (Call)
    locator_model = (CaregiverLocator, 'subject_identifier')
#     consent_model = (SubjectConsent, 'subject_identifier')
    alternative_locator_filter = 'study_maternal_identifier'
    log_entry_model = LogEntry
    log_model = Log
    interval = DAILY
