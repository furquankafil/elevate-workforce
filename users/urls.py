from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Account Registration Flow
    path('register/candidate/', views.register_candidate_view, name='register_candidate'),
    #path('register/employer/', views.register_employer_view, name='register_employer'),
    
    # Session Management
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Profile Controls
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_update_view, name='profile'),
    path('password/', views.change_password_view, name='change_password'),
]