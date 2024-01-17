import pytz
from datetime import datetime, timedelta, date, time
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from django.core.management import BaseCommand
from django.apps import apps as django_apps
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
        turning_six_months_children = self.populate_children_turning_six_months()
        self.create_reminders(turning_six_months_children)

    def generate_weeks_between_dates(self, start_date, end_date):
        current_date = start_date
        target_weeks = []

        while current_date <= end_date:
            target_week_start = current_date
            target_week_end = current_date + timedelta(days=7)
            target_weeks.append((target_week_start, target_week_end))
            current_date += timedelta(weeks=1)

        return target_weeks

    def populate_children_turning_six_months(self):
        turning_six_months_children = defaultdict(lambda: set())

        edc_protocol = django_apps.get_app_config('edc_protocol')

        start_date = date(2023, 10, 2)
        end_date = edc_protocol.study_close_datetime.date()

        weeks_between_dates = self.generate_weeks_between_dates(
            start_date, end_date)

        for child in MotherChildConsent.objects.only(
                'subject_identifier', 'child_dob'):

            if not child.child_dob:
                continue

            six_months_date = child.child_dob + relativedelta(months=6)

            for target_week_start, target_week_end in weeks_between_dates:

                if target_week_start <= six_months_date <= target_week_end:

                    turning_six_months_children[target_week_start.isoformat()].add(
                        child.subject_identifier)

        return turning_six_months_children

    def create_reminders(self, turning_six_months_children):
        new_reminder_objs = []

        for monday_iso_date, subject_identifiers in turning_six_months_children.items():

            monday_date = date.fromisoformat(
                monday_iso_date) + timedelta(days=1)

            title = "FACET Children turning 6 months next week"
            note = "No children tunrning 6 months next week"

            if subject_identifiers:
                note = f'The following PIDs are for children turn 6 months next week - {", ".join(subject_identifiers)}'

            try:
                Reminder.objects.get(
                    title=title,
                    start_date=monday_date,
                )

            except Reminder.DoesNotExist:

                reminder_obj = Reminder(
                    start_date=monday_date,
                    title=title,
                    note=note,
                    datetime=datetime.combine(monday_date, time(
                        0, 0)).astimezone(pytz.UTC),
                    repeat=ONCE,
                    remainder_time=time(0, 0,).replace(tzinfo=None),)
                new_reminder_objs.append(reminder_obj)

        Reminder.objects.bulk_create(new_reminder_objs)
