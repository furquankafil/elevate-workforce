from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse

from .forms import (
    CandidateRegisterForm, EmployerRegisterForm, CustomLoginForm, 
    CandidateProfileForm, EmployerProfileForm, UserUpdateForm
)
from .models import CandidateProfile, EmployerProfile
from jobs.models import Application, SavedJob, Job, Interview


def register_candidate_view(request):
    """
    Onboarding view for Candidates wishing to apply for international openings.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
        
    if request.method == 'POST':
        form = CandidateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. You can now login and complete your profile.")
            return redirect('users:login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CandidateRegisterForm()
    return render(request, 'users/register.html', {
        'form': form,
        'role_title': 'Candidate'
    })


def register_employer_view(request):
    """
    Employer registration is disabled in production.
    New employer accounts are created only by the administrator.
    """

    if request.user.is_authenticated:
        return redirect('users:dashboard')

    messages.warning(
        request,
        "Employer registration is currently disabled. "
        "Please contact Elevate Workforce to become an approved hiring partner."
    )

    return redirect('users:login')


def login_view(request):
    """
    Consolidated authentication login portal. Automatically determines user roles 
    and handles redirect target vectors.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Invalid credentials. Please verify your details.")
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Gracefully logs the user out of their session.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:index')


@login_required
def dashboard_view(request):
    """
    Core portal dispatcher. Inspects the authenticated user's role 
    and redirects/renders the respective candidate or employer workspace.
    """
    user = request.user
    if user.is_candidate:
        profile, created = CandidateProfile.objects.get_or_create(user=user)
        applied_jobs = Application.objects.filter(candidate=profile)
        saved_jobs = SavedJob.objects.filter(candidate=profile)
        interviews = Interview.objects.filter(application__candidate=profile)
        
        context = {
            'profile': profile,
            'applied_jobs': applied_jobs,
            'saved_jobs': saved_jobs,
            'interviews': interviews,
        }
        return render(request, 'users/dashboard_candidate.html', context)
        
    elif user.is_employer:
        profile, created = EmployerProfile.objects.get_or_create(
            user=user, 
            defaults={'company_name': user.get_full_name() or f"Company-{user.id}"}
        )
        posted_jobs = Job.objects.filter(employer=profile)
        job_ids = posted_jobs.values_list('id', flat=True)
        applications = Application.objects.filter(job_id__in=job_ids).select_related('job', 'candidate__user')
        
        context = {
            'profile': profile,
            'posted_jobs': posted_jobs,
            'applications': applications,
        }
        return render(request, 'users/dashboard_employer.html', context)
    
    else:
        # Fallback view for staff/admin-only users
        return redirect('admin:index')


@login_required
def profile_update_view(request):
    """
    Handles user account parameters and physical profile assets (Resumes, bio matrices, logos).
    """
    user = request.user
    user_form = UserUpdateForm(instance=user)
    profile_form = None

    if user.is_candidate:
        profile, created = CandidateProfile.objects.get_or_create(user=user)
        profile_form = CandidateProfileForm(instance=profile)
    elif user.is_employer:
        profile, created = EmployerProfile.objects.get_or_create(
            user=user, 
            defaults={'company_name': user.get_full_name() or f"Company-{user.id}"}
        )
        profile_form = EmployerProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        if user.is_candidate:
            profile_form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
        elif user.is_employer:
            profile_form = EmployerProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and (profile_form and profile_form.is_valid()):
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile updates have been successfully saved.")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Could not update profile. Please verify your fields.")

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def change_password_view(request):
    """
    Enables users to update their active credentials securely.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, "Your password has been updated.")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Failed to update password. Correct errors below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})