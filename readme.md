# django-toolbox-view

A staff-only Django page that finds "toolbox" functions in your installed apps and shows each one as a button.
Clicking a button runs the function: directly in the request, or as a Celery task in a progress modal. You can
also ask the user to confirm first.

It's useful for the one-off admin jobs every project accumulates, such as rebuilding caches, re-importing data
or producing reports. Each job is a small class, with no view, URL or template to write.

Built on [django-ajax-helpers](https://github.com/jonesim/django-ajax-helpers),
[django-nested-modals](https://github.com/jonesim/django-modals) and
[django-tab-menus](https://github.com/jonesim/django-menus).

## Installation

```bash
pip install django-toolbox-view
```

Celery is only needed for functions that run as tasks (see below).

```python
# settings.py
INSTALLED_APPS = [
    ...
    'ajax_helpers',
    'django_modals',
    'django_menus',
    'toolbox_view',
]
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    ...
    path('toolbox/', include('toolbox_view.urls')),   # namespace 'toolbox'
]
```

This gives the toolbox page at `toolbox/toolbox/` (URL name `toolbox:toolbox`) and the task modal it uses
(`toolbox:toolbox_task`).

## Writing toolbox functions

Add a `toolbox` package to any installed app. Every `.py` file in it is scanned, and each `ToolBoxBase` subclass
found there becomes a button. A single `toolbox.py` module works too.

```
myapp/
    toolbox/
        __init__.py
        maintenance.py
```

```python
# myapp/toolbox/maintenance.py
from toolbox_view import ToolBoxBase


class ClearCache(ToolBoxBase):
    button_text = 'Clear cache'

    def button_function(self):
        cache.clear()
        return self.command_response('message', text='Cache cleared')
```

`button_function` runs in an AJAX request, and `self.request` is available. Return a
[django-ajax-helpers](https://github.com/jonesim/django-ajax-helpers) command response:
`self.command_response('message', text=...)`, `self.command_response('reload')` and so on.

A class imported into a toolbox file also gets a button, so tools can live elsewhere and be listed from the
toolbox package. Each class gets one button, however many toolbox files import it. Classes without
`button_text`, such as a shared base class, don't get a button.

### Class attributes

| Attribute | Default | Purpose |
|---|---|---|
| `button_text` | `None` | Button label |
| `button_colour` | `'primary'`, or `'success'` when `task = True` | Bootstrap colour suffix (`btn-<colour>`) |
| `tooltip` | none | Tooltip shown on the button |
| `button_group` | the app's `verbose_name` | Heading the button is grouped under; groups are sorted by name |
| `task` | `False` | Run as a Celery task (see below) |

### Per-button permissions

Override the `button_permission` classmethod to hide a button from some users. A button that is hidden from a
user can't be run by that user either.

```python
class PurgeAuditLog(ToolBoxBase):
    button_text = 'Purge audit log'

    @classmethod
    def button_permission(cls, request):
        return request.user.is_superuser
```

### Asking for confirmation

```python
from toolbox_view.modal_confirm import ConfirmToolbox


class ResetDemoData(ToolBoxBase):
    button_text = 'Reset demo data'

    @ConfirmToolbox(message='This deletes all demo data. Continue?')
    def button_function(self):
        ...
```

`ConfirmToolbox` also takes `title` (default `'Warning'`) and `icon_type`: `'warning'` (default),
`'question'`, or anything else for no icon. It works with `task = True` too: the task starts once the user
confirms.

## Running as a Celery task

Set `task = True` for long-running jobs. The button opens a modal, the function runs in a Celery worker, and
the modal shows progress until the task finishes.

```python
class RebuildIndex(ToolBoxBase):
    button_text = 'Rebuild search index'
    task = True

    def button_function(self):
        self.update_message('Rebuilding index')
        for n, item in enumerate(items, 1):
            ...
            self.add_task_message(f'Indexed {n} of {len(items)}')
        return [ajax_command('message', text='Index rebuilt')]
```

- `self.update_message(text)` replaces the heading line in the modal.
- `self.add_task_message(text)` appends a line; the modal shows the last 8.
- Return a list of `ajax_command(...)`s to run when the task completes. The modal closes first. If you return
  anything else, a "Finished Executing" message is shown.
- `self.request` is **not** available inside a task.

This needs Celery installed (`pip install celery`) and a configured Celery app that autodiscovers tasks
(`app.autodiscover_tasks()`), so `toolbox_view.tasks` is registered, plus a running worker and a result backend.
Without Celery the task URL isn't registered, and clicking a `task = True` button raises `ImproperlyConfigured`.

## Access control

The page is limited to staff (`request.user.is_staff`). To change that, subclass `Toolbox`, override
`test_func`, and route your own URL to it. Include `AjaxHelpers` in the subclass, as the shipped `SimpleToolbox`
does:

```python
from ajax_helpers.mixins import AjaxHelpers
from toolbox_view.views import Toolbox


class OpsToolbox(AjaxHelpers, Toolbox):
    def test_func(self):
        return self.request.user.groups.filter(name='ops').exists()
```

You can have several toolbox views with different rules. A clicked button is looked up among that view's own
`function_classes`, and its `button_permission` is checked, so the client can't name any other code to run.

Task buttons run through a separate modal URL, but you don't need to configure it. Once the view has run those
checks, it gives the modal a URL carrying a token signed with `SECRET_KEY` for the current user. The modal
accepts only that token, for that user, and only within 5 minutes of the click
(`ToolboxTaskModal.token_max_age`). A task that runs longer still reports its result.

## Customising the page

`toolbox/base.html` is a minimal page that renders `{{ tool_box_buttons }}`. To put the toolbox inside your own
layout, subclass `Toolbox` and set `template_name`. The demo project's `TabToolboxView` does this as a tab in a
django-tab-menus page.

## Helpers

- **`toolbox_view.report.ReportFile(filename, xl=False, sheet=None, folder='reports/')`** writes a timestamped
  text/CSV file, or an `.xlsx` with `xl=True` (needs `openpyxl`), to `default_storage`. Use `write`,
  `write_ln` and `write_csv_line`, then `close()`.
- **`toolbox_view.bulk_save.BulkSave(model=..., store_ids=False)`** batches `append(instance)` calls into
  `bulk_create` every 100 records and reports progress when given `modal_task`. Call `finish()` at the end.
- **`toolbox_view.bulk_save.BulkSaveSQL(fields=[...], model=..., model_id=None)`** is the same idea using one raw
  `INSERT`. `model_id` adds `RETURNING` (PostgreSQL). Numbers are written as-is; everything else, including
  dates and datetimes (ISO format), is quoted and escaped by hand, so only use it with trusted data.
- **`toolbox_view.bulk_save.delete_reset(*models, query_filter=None, raw=False)`** deletes rows and resets the
  models' primary-key sequences.
- **`toolbox_view.helpers.task_print(task, message)`** reports progress to a task modal, or prints when there is
  no task.

## Demo project

`django_examples/` is a demo project with example toolbox functions in `examples/toolbox/`. To run it with
Redis and a Celery worker:

```bash
docker compose up
```

Then open http://localhost:8027/ (the tabbed `TabToolboxView`) or http://localhost:8027/toolbox/toolbox/ (the
plain staff-only page). Create a staff user with `docker compose exec django python manage.py createsuperuser`.
