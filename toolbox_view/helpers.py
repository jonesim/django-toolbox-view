import importlib
import os


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
    classes = []
    module_name = module.__name__
    module_dir = module.__path__[0]
    files = [f for f in os.listdir(module_dir) if f.endswith('.py') and not f.startswith('__')]
    for file_name in files:
        module_file = os.path.splitext(file_name)[0]
        module = importlib.import_module(f'{module_name}.{module_file}')
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and obj != module_class and issubclass(obj, module_class):
                classes.append(obj)
    return classes
