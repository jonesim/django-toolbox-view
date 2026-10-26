from django.urls import path, include

from toolbox_view.modals import ToolboxTaskModal
from toolbox_view.views import SimpleToolbox

try:
    from toolbox_view.tasks import toolbox_task
except ModuleNotFoundError as e:
    if e.name != 'celery':
        raise
    toolbox_task = None  # Celery is optional; without it there is no task URL and task = True tools can't run

app_name = 'toolbox'

# Not the old task/toolbox/<slug>/ path, which projects may still shadow with their own route
modal_urls = [
    path('task/toolbox-run/<str:token>/', ToolboxTaskModal.as_view(task=toolbox_task), name='toolbox_task'),
] if toolbox_task else []

urlpatterns = [
    path('modal/', include(modal_urls)),
    path('toolbox/', SimpleToolbox.as_view(), name='toolbox'),
]