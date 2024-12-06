from django.urls import path
from . import views
from .views import AdminCommentsView, approve_comment, reject_comment


urlpatterns = [
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('approve-post/<int:pk>/', views.approve_post, name='approve-post'),
    path('admin-dashboard/comments/', AdminCommentsView.as_view(), name='admin-dashboard-comments'),
    path('approve-comment/<int:pk>/', approve_comment, name='approve-comment'),
    path('reject-comment/<int:pk>/', reject_comment, name='reject-comment'),
]
