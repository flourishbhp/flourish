from django.views.generic import TemplateView
from edc_base.view_mixins import AdministrationViewMixin
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from django.forms import model_to_dict
from django.http import JsonResponse


class AdministrationView(EdcBaseViewMixin, NavbarViewMixin,
                         AdministrationViewMixin, TemplateView):

    navbar_name = 'flourish'
    navbar_selected_item = 'administration'


