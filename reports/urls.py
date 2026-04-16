from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('timesheet/', views.generate_timesheet, name='generate_timesheet'),
    path('journal/', views.generate_journal_report, name='generate_journal'),
    path('report/<int:pk>/', views.view_report, name='view_report'),
]
