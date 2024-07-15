import importlib

from ajax_helpers.mixins import AjaxHelpers
from ajax_helpers.utils import ajax_command
from django.apps import apps
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django_menus.menu import MenuItem, HtmlMenu
from django_modals.messages import AjaxMessagesMixin

from toolbox_view import ToolBoxBase
from toolbox_view.helpers import import_classes_from_module


class Toolbox(AjaxMessagesMixin, TemplateView):
    template_name = 'toolbox/base.html'
    menu_display = 'Toolbox'

    def __init__(self, *args, **kwargs):
        self._classes = None
        super().__init__(*args, **kwargs)

    @property
    def function_classes(self):
        if self._classes is None:
            self._classes = {}
            for a in apps.app_configs.values():
                try:
                    toolbox = importlib.import_module('.toolbox', a.module.__package__)
                    self._classes[a.verbose_name] = import_classes_from_module(toolbox, ToolBoxBase)
                except ModuleNotFoundError:
                    pass
        return self._classes

    @staticmethod
    def direct_button(function_class):
        return MenuItem(ajax_command('ajax_post', data={'button': 'execute', 'module': function_class.__module__,
                                                        'class_name': function_class.__name__}),
                        function_class.button_text,
                        link_type=MenuItem.AJAX_COMMAND)

    @staticmethod
    def task_button(function_class):
        return MenuItem(f'toolbox:toolbox_task,'
                        f'module-{function_class.__module__}-'
                        f'class_name-{function_class.__name__}',
                        function_class.button_text, css_classes=f'mr-1 mb-1 btn btn-{function_class.button_colour}')

    def button_execute(self, class_name, module):
        function_class = getattr(importlib.import_module(f'{module}'), class_name)()
        function_class.request = self.request
        return function_class.button_function()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_dict = {}
        for k, v in self.function_classes.items():
            for b in v:
                b.app = k
                group_dict.setdefault(getattr(b, 'button_group', k), []).append(b)

        groups = list(group_dict.keys())
        groups.sort()
        menus = []
        for g in groups:
            buttons = [self.task_button(v) if v.task else self.direct_button(v) for v in group_dict[g]]
            if buttons:
                menus.append(f'<h4>{g}</h4>{HtmlMenu(template="buttons").add_items(*buttons).render()}')
        context['tool_box_buttons'] = mark_safe('<hr>'.join(menus))
        return context


class SimpleToolbox(AjaxHelpers, Toolbox):
    pass
