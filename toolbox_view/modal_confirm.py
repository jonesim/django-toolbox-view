import base64
import json

from ajax_helpers.utils import ajax_command
from django.http import JsonResponse
from django_modals.decorators import ConfirmAjaxMethod
from django_modals.helper import modal_button

from toolbox_view.helpers import task_url


class ConfirmToolbox(ConfirmAjaxMethod):
    title = 'Warning'
    icon_type = 'warning'

    def __init__(self, *args, use_json=False, **kwargs):
        if args:
            raise Exception('Decorator class ConfirmAjaxMethod must be an instance and have ()')
        self.use_json = use_json
        self.kwargs = kwargs

    @staticmethod
    def proc_message(message, **kwargs):
        return message

    @staticmethod
    def buttons(view, func, **kwargs):
        return [modal_button('Confirm',
                             ajax_command('ajax_post', data={'button': 'execute', 'module': view.__module__,
                                                             'class_name': view.__class__.__name__, 'confirm': 'True'}),
                             'btn-warning'),
                modal_button('Cancel', 'close', 'btn-secondary')]

    def get_html(self, message, request, title, buttons):
        from django_modals.messages import warning_modal, message_modal
        icon_type = self.kwargs.get('icon_type', self.icon_type)
        if icon_type == 'warning':
            result = warning_modal(message, request, title=title, buttons=buttons)
        elif icon_type == 'question':
            icon = '<i class="fas fa-question-circle fa-2x"></i>'
            result = message_modal(message, request, title=title, buttons=buttons, icon=icon)
        else:
            result = message_modal(message, request, title=title, buttons=buttons)
        return result

    def __call__(self, _func, **kwargs):
        def method(view, _ajax=True, **kwargs):
            if kwargs.get('confirm'):
                view.add_command('close')
                if self.use_json:
                    kwargs = json.loads(base64.urlsafe_b64decode(kwargs['json_data']))
                confirm = kwargs.pop('confirm', None)
                if getattr(view, 'task', False) and confirm != 'task':
                    return view.command_response('show_modal', modal=task_url(view.__class__.__module__,
                                                                              view.__class__.__name__))
                return _func(view, **kwargs)
            view.request.method = 'GET'
            message = self.proc_message(self.kwargs.get('message', 'Are you sure?'), **kwargs)
            title = self.kwargs.get('title', self.title)
            if self.use_json:
                kwargs = {'json_data': base64.urlsafe_b64encode(json.dumps(kwargs).encode('utf8')).decode('utf-8')}
            buttons = self.buttons(view, _func, **kwargs)
            return JsonResponse([{
                'function': 'modal_html',
                'html': self.get_html(message, view.request, title=title, buttons=buttons)
            }], safe=False)
        return method
