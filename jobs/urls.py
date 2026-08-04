from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # 1. Base Job List Index
    path('', views.job_list_view, name='job_list'),
    
    # 2. Employer Post Route
    path('post/', views.post_job_view, name='post_job'),
    
    # 3. Dynamic Destination Detail Page (Saves routes to specific locations)
    path('destinations/<slug:slug>/', views.destination_detail_view, name='destination_detail'),
    
    # 4. Dynamic Catch-All Job Specific Actions (Must be at the bottom)
    path('<slug:slug>/', views.job_detail_view, name='job_detail'),
    path('<slug:slug>/apply/', views.apply_job_view, name='apply_job'),
    path('<slug:slug>/save/', views.save_job_view, name='save_job'),
    
    # 5. Employer Sourcing & Screening Pathways
    path('applications/<int:application_id>/status/', views.update_application_status_view, name='update_application_status'),
    path('applications/<int:application_id>/schedule-interview/', views.schedule_interview_view, name='schedule_interview'),
]