import json
import os

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Migrate data from choice field to m2m field'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='Data fine path, json file')

    def handle(self, *args, **kwargs):
        updated = 0
        file_path = os.path.join(
            settings.BASE_DIR,
            'maternalarvpostadherence.json')
        data = self.data(file_path=file_path)

        arv_post_adherence = 'flourish_caregiver.maternalarvpostadherence'
        arv_post_adherence_cls = django_apps.get_model(arv_post_adherence)

        for data_item in data:
            data_options = data_item.get('fields')
            try:
                post_adherence = arv_post_adherence_cls.objects.get(
                    id=data_item.get('pk'))
            except arv_post_adherence_cls.DoesNotExist:
                pass
            else:
                interruption_reason_cls = django_apps.get_model(
                    'flourish_caregiver.arvinterruptionreasons')
                interruption_reason = data_options.get('interruption_reason')
                try:
                    reason_obj = interruption_reason_cls.objects.get(
                        short_name=interruption_reason)
                except interruption_reason_cls.DoesNotExist:
                    pass
                else:
                    post_adherence.interruption_reason.add(reason_obj)
                    updated += 1
        print(f'**finished migration.')
        print(f'**updated {updated} records.')

    def data(self, file_path=None):
        with open(file_path) as f:
            data = json.load(f)
        self.stdout.write(
            self.style.SUCCESS(
                f'**starting migration of maternalarvpostadherence interruption reasons.'))
        return data
