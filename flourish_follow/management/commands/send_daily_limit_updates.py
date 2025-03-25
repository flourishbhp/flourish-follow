from django.core.management.base import BaseCommand


from ...utils import send_daily_cohort_limit_updates


class Command(BaseCommand):
    help = 'Send daily cohort limit email updates'

    def handle(self, *args, **kwargs):
        send_daily_cohort_limit_updates()
