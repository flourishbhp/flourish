from edc_list_data import PreloadData
from django.core.management.base import BaseCommand
from flourish_caregiver.list_data import list_data as caregiver_list_data
from flourish_child.list_data import list_data as child_list_data
from flourish_facet.list_data import list_data as facet_list_data


class Command(BaseCommand):
    help = 'Load flourish list data'

    def handle(self, *args, **kwargs):
        PreloadData(list_data=caregiver_list_data)
        PreloadData(list_data=facet_list_data)
        PreloadData(list_data=child_list_data)

        self.stdout.write(self.style.SUCCESS(
            f'Flourish List data successfully loaded.'))
