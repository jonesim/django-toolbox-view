from ajax_helpers.utils import ajax_command
from django.core.exceptions import PermissionDenied
from django_modals.task_modals import TaskModal

from toolbox_view.helpers import read_task_token


class ToolboxTaskModal(TaskModal):
    """
    Runs a toolbox function as a Celery task.  The toolbox view that showed the button issues this modal's URL
    (task_url) with a signed token naming the user and function, so the modal runs exactly what that view allowed,
    whatever its test_func and function_classes.  The token's age is only checked when the modal opens and when
    the task starts, not on every check_result poll, so a long task still reports its result.
    """
    token_max_age = 300

    def process_slug_kwargs(self):
        self.slug = read_task_token(self.kwargs['token'], self.request)
        if self.slug is None:
            raise PermissionDenied()
        return super().process_slug_kwargs()

    def token_expired(self):
        return read_task_token(self.kwargs['token'], self.request, self.token_max_age) is None

    def get(self, request, *args, **kwargs):
        if self.token_expired():
            raise PermissionDenied()
        return super().get(request, *args, **kwargs)

    def ajax_start_task(self, **kwargs):
        if self.token_expired():
            return self.command_response([ajax_command('close'),
                                          ajax_command('message', text='Expired, please click the button again')])
        return super().ajax_start_task(**kwargs)
