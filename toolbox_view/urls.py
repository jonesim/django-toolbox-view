from django.urls import path, include
from django_modals.task_modals import TaskModal

from toolbox_view.tasks import toolbox_task
from toolbox_view.views import SimpleToolbox

app_name = 'toolbox'

modal_urls = [
    path('task/toolbox/<str:slug>/', TaskModal.as_view(task=toolbox_task), name='toolbox_task'),
]

urlpatterns = [
    path('modal/', include(modal_urls)),
    path('toolbox/', SimpleToolbox.as_view(), name='toolbox'),
]