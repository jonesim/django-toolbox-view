from ajax_helpers.mixins import AjaxHelpers

from toolbox_view.helpers import task_print


class ToolBoxBase(AjaxHelpers):
    button_text = None
    task = False

    @property
    def button_colour(self):
        return 'success' if self.task else 'primary'

    def button_function(self):
        pass

    def __init__(self, modal_task=None):
        self.modal_task = modal_task
        self.task_messages = []
        self.base_message = ''
        self.report = None
        super().__init__()

    # noinspection PyUnusedLocal
    @classmethod
    def button_permission(cls, request):
        return True

    def update_message(self, base_message=None):
        if base_message is not None:
            self.base_message = base_message
        task_print(self.modal_task, f'{self.base_message}<br>{"<br><br>".join(self.task_messages[-8:])}')

    def add_task_message(self, message):
        self.task_messages.append(message)
        self.update_message()

