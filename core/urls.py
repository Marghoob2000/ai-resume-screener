# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This line was missing. It makes the job list your homepage.
    path('', views.job_list, name='job_list'),

    # This line for the detail page is already correct.
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
]