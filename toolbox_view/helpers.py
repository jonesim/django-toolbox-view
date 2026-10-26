import importlib
import os

from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse


def task_print(task_object, message):
    if task_object:
        if hasattr(task_object, 'modal_task'):
            task_object = task_object.modal_task
        title = getattr(task_object, 'task_title', '')
        task_object.update_state(
            state='PROGRESS', meta={'message': f'{title}<br>{message}'}
        )
    else:
        print(message)


def import_classes_from_module(module, module_class=type):
    if hasattr(module, '__path__'):
        files = [f for f in os.listdir(module.__path__[0]) if f.endswith('.py') and not f.startswith('__')]
        modules = [importlib.import_module(f'{module.__name__}.{os.path.splitext(f)[0]}') for f in files]
    else:
        modules = [module]
    classes = []
    for module in modules:
        for name, obj in module.__dict__.items():
            if (isinstance(obj, type) and obj != module_class and issubclass(obj, module_class)
                    and obj not in classes):
                classes.append(obj)
    return classes


def toolbox_classes():
    """
    The ToolBoxBase subclasses found in each installed app's toolbox package, keyed by the app's verbose_name.
    Classes without button_text (such as shared base classes) are left out.
    """
    from django.apps import apps
    from toolbox_view.toolbox_base import ToolBoxBase

    classes = {}
    for a in apps.app_configs.values():
        try:
            toolbox = importlib.import_module('.toolbox', a.module.__package__)
        except ModuleNotFoundError as e:
            # Only an app without a toolbox is skipped; a missing import inside a toolbox file is raised
            if e.name != f'{a.module.__package__}.toolbox':
                raise
            continue
        classes[a.verbose_name] = [c for c in import_classes_from_module(toolbox, ToolBoxBase) if c.button_text]
    return classes


TASK_TOKEN_SALT = 'toolbox_view.task'


def task_url(module, class_name, request):
    """
    The task modal URL for a toolbox function.  Only call it once request has passed the toolbox view's test_func
    and the function's button_permission: the URL carries a token, signed for request's user, that the modal
    accepts in place of repeating those checks.
    """
    token = signing.TimestampSigner(salt=TASK_TOKEN_SALT).sign_object(
        {'user': request.user.pk, 'module': module, 'class_name': class_name})
    try:
        return reverse('toolbox:toolbox_task', kwargs={'token': token})
    except NoReverseMatch:
        raise ImproperlyConfigured(f'{module}.{class_name} has task = True, which needs Celery installed and '
                                   f'toolbox_view.urls included (URL name toolbox:toolbox_task)') from None


def read_task_token(token, request, max_age=None):
    """
    The module and class_name from a task_url token, or None if it isn't validly signed for request's user, or
    is older than max_age seconds.
    """
    try:
        data = signing.TimestampSigner(salt=TASK_TOKEN_SALT).unsign_object(token, max_age=max_age)
    except signing.BadSignature:
        return None
    if data.get('user') != request.user.pk:
        return None
    return {'module': data['module'], 'class_name': data['class_name']}


def has_confirm(func):
    return getattr(func, 'confirm_toolbox', False)
