from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from flourish_caregiver.load_cohort_schedules import flourish_schedules
from django.core.exceptions import MultipleObjectsReturned


class Command(BaseCommand):
    help = ('This creates up-to-date instances of cohort schedules objects, '
            'incase of an update to the visit schedules')

    def handle(self, *args, **kwargs):
        """ Creates or updates cohort schedule objects based on the schedule_name.
        """
        updated = 0
        creates = 0
        for schedule in flourish_schedules:
            schedule_name = schedule.pop('schedule_name', None)
            try:
                _, created = self.cohort_schedule_cls.objects.update_or_create(
                    schedule_name=schedule_name,
                    defaults=schedule)
            except MultipleObjectsReturned:
                print(schedule_name)
                break
            if created:
                creates += 1
                continue
            updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Total records updated: {updated}, and created: {creates}'))

    @property
    def cohort_schedule_cls(self):
        return django_apps.get_model('flourish_caregiver.cohortschedules')
