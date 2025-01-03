from ajax_helpers.utils import ajax_command
from django_modals.decorators import ConfirmAjaxMethod
from django_modals.helper import modal_button


class ConfirmToolbox(ConfirmAjaxMethod):

    @staticmethod
    def buttons(view, func, **kwargs):
        return [modal_button('Confirm',
                             ajax_command('ajax_post', data={'button': 'execute', 'module': view.__module__,
                                                             'class_name': view.__class__.__name__, 'confirm': 'True'}),
                             'btn-warning'),
                modal_button('Cancel', 'close', 'btn-secondary')]
