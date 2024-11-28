from django.urls import path

from magic_forum.common.views import test_view

urlpatterns = [
    path('', test_view)
]