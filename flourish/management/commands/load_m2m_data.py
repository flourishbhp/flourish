import json
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from flourish_caregiver import old_list_data
from flourish_child import old_list_data as child_old_list


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='Data fine path, csv file')

    def handle(self, *args, **kwargs):
        """ Loads data from JSON file, and create a mapping of the old m2m list data
            to the new based on the m2m field(s) on the data items. Then updates
            the new m2m value to an object of the already existing data object.
        """
        updated = 0
        file_path = kwargs['file_path']
        # Read data from JSON file
        data = self.data(file_path=file_path)

        m2m_models = {}

        # Get all m2m models from `flourish` app configs, update to dictionary
        # {app_label: models_list} key, value pair.
        app_configs = [app_model for app_model in list(django_apps.get_app_configs()) if app_model.models and 'flourish' in app_model.label]
        for app_config in app_configs:
            m2m_models.update(
                {f'{app_config.label}':
                 [m2m for m2m in app_config.models.keys() if '_' in m2m]})

        for data_item in data:
            record_id = data_item.get('pk')
            model = data_item.get('model')
            model_obj = self.get_model_obj(model_name=model, key='pk', value=record_id)

            label, model_name = model.split('.') if model else ['', '']

            # Get m2m fields existing/captured for the data record.
            app_m2m = [field for field in m2m_models.get(label) if model_name in field]
            m2m_fields = [field for field in app_m2m if model_name in field]

            fields_data = data_item.get('fields')
            for field in m2m_fields:
                m2m_field = field.replace(f'{model_name}_', '')
                m2m_name = getattr(django_apps.get_model(model), m2m_field).field.related_model._meta.label

                # Represented as a list of a list on the data [['value']]
                old_values = fields_data.get(m2m_field)

                self.update_m2m_data(
                    model_obj, field_name=m2m_field, old_values=old_values, model_name=m2m_name.lower())
            updated += 1
        self.stdout.write(self.style.WARNING(f'Total records updated: {updated}'))

    def get_model_obj(self, model_name=None, key=None, value=None):
        """Get model object, using key and value.
        """
        model_cls = django_apps.get_model(model_name)
        try:
            obj = model_cls.objects.get(**{f'{key}': value})
        except model_cls.DoesNotExist:
            return None
        else:
            return obj

    def update_m2m_data(self, obj, field_name=None, old_values=None, model_name=None):
        """ Retrieve old and new list data to create a mapping dict of the {'old': 'new'}
            Get the data representation of the old value(s) as a mapping of the
            new as a list model object, and update the `main` model object with
            the m2m list model objects.
        """
        old_list = self.old_list_data(model_name=model_name)
        new_list = self.new_list_data(model_name=model_name)

        list_data_map = dict(zip(old_list, new_list))
        for value in old_values:
            new_value = list_data_map.get(value[0])
            m2m_obj = self.get_model_obj(
                model_name=model_name, key='short_name', value=new_value)
            try:
                m2m_manger = getattr(obj, field_name)
            except AttributeError:
                self.stdout.write(self.style.ERROR(f'Failed {getattr(obj, "id", obj)}, {field_name}'))
            else:
                m2m_manger.add(m2m_obj)
                self.stdout.write(self.style.SUCCESS(
                    f'Updated {obj.id}, {field_name}: value => {new_value}'))

    def old_list_data(self, model_name=None):
        old_list_data.list_data.update(child_old_list.list_data)
        values = old_list_data.list_data.get(model_name)
        return [value[0] for value in values]

    def new_list_data(self, model_name=None):
        model_cls = django_apps.get_model(model_name)
        qs = model_cls.objects.order_by('created').values_list('short_name', flat=True)
        return list(qs)

    def data(self, file_path=None):
        json_file = open(file_path)
        data = json.load(json_file)
        json_file.close()
        self.stdout.write(self.style.SUCCESS(
            f'Total records imported: {len(data)}'))
        return data
