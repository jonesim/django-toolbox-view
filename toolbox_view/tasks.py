import importlib

from ajax_helpers.utils import ajax_command
from celery import shared_task

from toolbox_view.helpers import has_confirm
from toolbox_view.toolbox_base import ToolBoxBase


@shared_task(bind=True)
def toolbox_task(self, config=False, slug=None, **_kwargs):
    if config:
        return {'progress': False, 'message': 'Running ', 'title': 'Please wait....'}
    # slug comes from the modal's signed token, so it names a function a toolbox view allowed
    function_class = getattr(importlib.import_module(slug['module']), slug['class_name'], None)
    if not isinstance(function_class, type) or not issubclass(function_class, ToolBoxBase):
        raise ValueError(f'Not a toolbox function: {slug["module"]}.{slug["class_name"]}')
    function = function_class(modal_task=self).button_function
    commands = function(confirm='task') if has_confirm(function) else function()
    if not isinstance(commands, list):
        commands = [ajax_command('close'),
                    ajax_command('message', text='Finished Executing \n\n' + slug['class_name'])]
    else:
        commands.insert(0, ajax_command('close'))
    return {'commands': commands}
