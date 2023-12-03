import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from edc_base.utils import age
from django.core.management import BaseCommand
from flourish_facet.models import MotherChildConsent
from flourish_calendar.models import Reminder
from flourish_calendar.constants import ONCE


class Command(BaseCommand):
    help = '''\
    Used to extract all the subject identifiers,
    from both the caregiver and the child
    '''

    def children_pids(self):
        MotherChildConsent.objects.values_list('sub')

    def handle(self, *args, **options):
        facet_child_consents = MotherChildConsent.objects.all()

        next_week_dates = self.generate_next_week_dates()

        # monday (of next week)
        first_day = next_week_dates[0]

        # sunday (of next week)
        last_day = next_week_dates[-1]

        subject_identifiers = []

        for consent in facet_child_consents:

            date_after_months = consent.child_dob + relativedelta(months=6)

            if first_day <= date_after_months <= last_day:
                subject_identifiers.append(consent.subject_identifier)

        if subject_identifiers:
            reminder = Reminder()
            reminder.title = "FACET Children turning 6 months next week"
            reminder.start_date = datetime.now().date()
            reminder.repeat = ONCE
            reminder.note = f'''The following PIDs are for children turn \
                6 months next week\n {', '.join(subject_identifiers)}'''
            reminder.remainder_time = datetime.now()
            reminder.save()
        else:
            reminder = Reminder()
            reminder.title = "FACET Children turning 6 months next week"
            reminder.start_date = datetime.now().date()
            reminder.repeat = ONCE
            reminder.note = '''No children tunrning 6 months next week'''
            reminder.remainder_time = datetime.now()
            reminder.save()

    @staticmethod
    def generate_next_week_dates():
        # Get the current date
        today = datetime.today()

        # Calculate the number of days until the next Monday
        days_until_next_monday = 7 - today.weekday()

        # Calculate the date for the next Monday
        next_monday = today + timedelta(days=days_until_next_monday)

        # Generate a list of dates for the next week (Monday to Sunday)
        next_week_dates = [(next_monday + timedelta(days=i)).date()
                           for i in range(7)]

        return next_week_dates
