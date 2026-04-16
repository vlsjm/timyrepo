from django.urls import path
from . import views

app_name = 'logging_app'

urlpatterns = [
    path('log/', views.log_hours, name='log_hours'),
    path('logs/', views.logs, name='logs'),
    path('log/<int:pk>/', views.log_detail, name='log_detail'),
    path('log/<int:pk>/edit/', views.edit_log, name='edit_log'),
    path('log/<int:pk>/delete/', views.delete_log, name='delete_log'),
]
