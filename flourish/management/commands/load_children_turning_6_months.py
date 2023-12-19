from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta, MO
from dateutil.rrule import rrule, DAILY
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

        # Calculate all the Mondays in the current month
        mondays = self.get_mondays_of_current_month()

        # Iterate through each Monday
        for monday in mondays:
            title = f"FACET Age calculation for {monday.strftime('%Y-%m-%d')}:\n"
            print(title)

            descriptions = []

            # Iterate through each child in the queryset
            for child in MotherChildConsent.objects.all():
                # Calculate age using dateutil.relativedelta
                age_delta = relativedelta(monday, child.child_dob)

                if age_delta.months == 6 and age_delta.years == 0:  # Considering turning 6 months
                    description = f"Child with PID {child.subject_identifier} born on {child.child_dob.strftime('%Y-%m-%d')} is turning 6 months (age: {age_delta.months} months)"

                    descriptions.append(description)

            if descriptions:
                reminder = Reminder()
                reminder.title = title
                reminder.start_date = monday.date()
                reminder.datetime = monday
                reminder.repeat = ONCE
                reminder.note = '\n'.join(descriptions)
                reminder.remainder_time = datetime.now().time()
                reminder.save()

    @staticmethod
    def get_mondays_of_current_month():
        today = date.today()
        first_day_of_month = today.replace(day=1)

        # Find all Mondays in the current month
        mondays = list(rrule(DAILY, dtstart=first_day_of_month,
                       until=first_day_of_month + relativedelta(day=31), byweekday=MO))

        return mondays
