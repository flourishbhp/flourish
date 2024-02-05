import os
from tqdm import tqdm
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError
from edc_base.model_mixins import ListModelMixin

from flourish_caregiver.admin_site import flourish_caregiver_admin
from flourish_child.admin_site import flourish_child_admin
from flourish_facet.admin_site import flourish_facet_admin

from flourish.tasks import run_exports

admin_site_map = {'flourish_child': flourish_child_admin,
                  'flourish_caregiver': flourish_caregiver_admin,
                  'flourish_facet': flourish_facet_admin}


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
                    raise CommandError(
                        f'Model not loaded/recognised {model_args}')
                else:
                    app_list.update(
                        {f'{model_cls._meta.model_name}': model_cls})
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
            intermediate_model = model_cls._meta.verbose_name.endswith(
                'relationship')
            if intermediate_model:
                continue
            # Check if model is inline model, by checking foreign key relation/m2one
            model_cls = model_cls._meta.label_lower
            try:
                run_exports.delay(model_cls, app_label)
                self.stdout.write(self.style.SUCCESS(
                    f'Begin export for {model_cls}'))
            except ValueError as e:
                self.stdout.write(
                    self.style.WARNING(f'{str(e)}'))

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

            if hasattr(model_admin_cls, 'export_as_csv'):
                """
                Can be used to exclude some models not needed in the exports
                by excluding the mixin from the model admin of interest
                """
                response = model_admin_cls.export_as_csv(
                    request=None, queryset=queryset)

                if response:
                    if response.status_code == 200:
                        if not os.path.exists(file_path):
                            os.makedirs(file_path)
                        with open(f'{file_path}/{model_admin_cls.get_export_filename()}.xlsx', 'wb') as file:
                            file.write(response.content)

                        self.stdout.write(
                            self.style.SUCCESS(f'Export complete for {model_cls._meta.verbose_name}'))
                    else:
                        response.raise_for_status()
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Empty response returned for {model_cls._meta.verbose_name}'))
