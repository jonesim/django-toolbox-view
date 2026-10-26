import base64
import json

from ajax_helpers.utils import ajax_command
from django_modals.decorators import ConfirmAjaxMethod
from django_modals.helper import modal_button

from toolbox_view.helpers import task_url


class ConfirmToolbox(ConfirmAjaxMethod):
    """
    Asks for confirmation before a toolbox button_function runs.  The wrapped method is marked confirm_toolbox,
    which has_confirm tests for: a subclass that overrides __call__ must keep that marker (functools.wraps does).
    """

    # Upstream only accepts use_json from django-nested-modals 0.0.25
    def __init__(self, *args, use_json=False, **kwargs):
        if args:
            raise Exception('Decorator class ConfirmToolbox must be an instance and have ()')
        self.use_json = use_json
        self.kwargs = kwargs

    @staticmethod
    def buttons(view, func, **kwargs):
        data = {**kwargs, 'button': 'execute', 'module': view.__module__, 'class_name': view.__class__.__name__,
                'confirm': 'True'}
        return [modal_button('Confirm', ajax_command('ajax_post', data=data), 'btn-warning'),
                modal_button('Cancel', 'close', 'btn-secondary')]

    def __call__(self, _func, **kwargs):
        def method(view, _ajax=True, **kwargs):
            confirm = kwargs.pop('confirm', None)
            if confirm:
                view.add_command('close')
                # A task is started with confirm='task' only, so there is no json_data to decode
                if self.use_json and 'json_data' in kwargs:
                    kwargs = json.loads(base64.urlsafe_b64decode(kwargs['json_data']))
                if getattr(view, 'task', False) and confirm != 'task':
                    return view.command_response('show_modal', modal=task_url(view.__class__.__module__,
                                                                              view.__class__.__name__,
                                                                              view.request))
                return _func(view, **kwargs)
            view.request.method = 'GET'
            message = self.proc_message(self.kwargs.get('message', 'Are you sure?'), **kwargs)
            title = self.kwargs.get('title', self.title)
            if self.use_json:
                kwargs = {'json_data': base64.urlsafe_b64encode(json.dumps(kwargs).encode('utf8')).decode('utf-8')}
            buttons = self.buttons(view, _func, **kwargs)
            return view.command_response('modal_html', html=self.get_html(message, view.request, title=title,
                                                                          buttons=buttons))
        method.confirm_toolbox = True
        return method
