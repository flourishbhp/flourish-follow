from faker import Faker
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NOT_APPLICABLE
from model_mommy.recipe import Recipe

from .models import Call, Log, LogEntry, WorkList

fake = Faker()

logentry = Recipe(
    LogEntry,
    appt=YES,
    appt_date=get_utcnow().date(),
    appt_grading='firm',
    appt_location='clinic',
    may_call=YES,
    home_visit=NOT_APPLICABLE)

log = Recipe(
    Log,)

call = Recipe(
    Call,)

worklist = Recipe(
    WorkList,)
