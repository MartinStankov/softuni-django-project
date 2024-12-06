from django.urls import path
from . import views


urlpatterns = [
    path('post/<int:post_id>/comment/', views.add_comment, name='add-comment'),
]
