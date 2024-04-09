from django.urls import path

from .views import TabToolboxView

urlpatterns = [
    path('', TabToolboxView.as_view(), name='subclassed_view'),
]
