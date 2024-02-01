from django.apps import apps as django_apps
from django.db.models import Q
from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from .statistics_mixin import StatisticsMixin
from edc_navbar import NavbarViewMixin


class HomeView(StatisticsMixin,
               NavbarViewMixin,
               TemplateView):

    template_name = 'flourish/home.html'
    navbar_name = 'flourish'
    navbar_selected_item = 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            flourish_consents=self.total_flourish_consents,
            flourish_assents=self.total_child_assents,
            child_consents=self.total_child_consents,
            continued_consents=self.total_continued_consents,
            total_caregiver_prev_study=self.total_caregiver_prev_study,
            total_child_prev=self.total_child_prev,
            total_all_preg_women=self.total_all_preg_women,
            total_consented_pregnant_women=self.total_consented_pregnant_women,
            total_currently_pregnant_women=self.total_currently_pregnant_women,
            total_maternal_delivery=self.total_maternal_delivery,
            total_prev_caregivers_offstudy=self.total_prev_caregivers_offstudy,
            total_prev_child_offstudy=self.total_prev_child_offstudy,
            total_caregivers_deaths=self.total_caregivers_deaths,
            total_child_deaths=self.total_child_deaths,
            total_prev_caregivers_deaths=self.total_prev_caregivers_deaths,
            total_prev_child_deaths=self.total_prev_child_deaths
        )
        return context
