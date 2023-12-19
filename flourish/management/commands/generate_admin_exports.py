import os
from tqdm import tqdm
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError
from edc_base.model_mixins import ListModelMixin

from flourish_caregiver.admin_site import flourish_caregiver_admin
from flourish_child.admin_site import flourish_child_admin


admin_site_map = {'flourish_child': flourish_child_admin,
                  'flourish_caregiver': flourish_caregiver_admin, }


class Command(BaseCommand):
    help = 'Run export method from model admin to generate csv data for all CRF and non-CRF models.'

    def add_arguments(self, parser):
        parser.add_argument(
            'args',
            metavar='app_label[.ModelName]',
            nargs='*',
            help='Exports data for a specified app_label or app_label.ModelName')
        
    def handle(self, *args, **kwargs):
        app_list = {}
        if not args:
            # Get all CRF models from `flourish_caregiver` and `flourish_child` app configs,
            # update to dictionary {model_name: models_cls} key, value pair.
            args = ('flourish_caregiver', 'flourish_child', )

        # Check args defined for specific app_label and/or model name(s)
        for model_args in args:
            try:
                _app_label, _model_name = model_args.split('.')
            except ValueError:
                # This is just an app - no model qualifier
                try:
                    app_config = django_apps.get_app_config(model_args)
                except LookupError as e:
                    raise CommandError(str(e))
                else:
                    app_list.update(app_config.models)
            else:
                # Assumes this is an app_label.model_name definition
                try:
                    model_cls = django_apps.get_model(model_args)
                except LookupError as e:
                    raise CommandError(f'Model not loaded/recognised {model_args}')
                else:
                    app_list.update({f'{model_cls._meta.model_name}': model_cls})
        self.exclude_rel_models(app_list)

    def exclude_rel_models(self, app_list):
        """ Restrict the export to only CRFs and enrolment forms, excludes m2m, inlines and any
            other relationship models that will be included as part of the main parent data.
            @param app_list: dictionary of model_name: model_cls
        """
        for _, model_cls in tqdm(app_list.items()):
            app_label = model_cls._meta.app_label
            # Check model class is m2m, skip
            if issubclass(model_cls, ListModelMixin):
                continue
            intermediate_model = model_cls._meta.verbose_name.endswith('relationship')
            if intermediate_model:
                continue
            # Check if model is inline model, by checking foreign key relation/m2one
            # inline_model = any([field.is_relation and field.many_to_one for field in model_cls._meta.get_fields()])
            
            self.stdout.write(self.style.SUCCESS(f'Begin export for {model_cls._meta.verbose_name}'))
            self.run_export(model_cls, app_label)
        
    def run_export(self, model_cls, app_label):
        """ Executes the csv model export method from admin export action(s) and writes response
            content to an excel file.
            @param model_cls: Specific model class definition
            @param app_label: Specific app label for the model class 
        """
        app_admin_site = admin_site_map.get(app_label, None)

        model_admin_cls = app_admin_site._registry.get(model_cls, None)

        queryset = model_cls.objects.all()

        if not model_admin_cls:
            self.stdout.write(
                self.style.WARNING(f'Model class not registered {model_cls._meta.verbose_name}'))
        elif not queryset.exists():
            self.stdout.write(
                self.style.ERROR(f'Empty queryset returned for {model_cls._meta.verbose_name}'))
        else:
            file_path = f'media/admin_exports/{app_label}'
            response = model_admin_cls.export_as_csv(request=None, queryset=queryset)

            if response.status_code == 200:
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open(f'{file_path}/{model_admin_cls.get_export_filename()}.xls', 'wb') as file:
                    file.write(response.content)
    
                self.stdout.write(
                    self.style.SUCCESS(f'Export complete for {model_cls._meta.verbose_name}'))
            else:
                response.raise_for_status()
