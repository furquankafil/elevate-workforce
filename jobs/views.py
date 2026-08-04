from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Destination, Category, Job, Application, SavedJob, Interview
from .forms import JobForm, InterviewForm
from users.models import CandidateProfile, EmployerProfile

def job_list_view(request):
    """
    Search-optimized filter engine for job posts.
    Handles paginated queries, categorizations, and international filters.
    Compatible with both 'destination' and legacy 'country' parameters.
    """
    jobs_query = Job.objects.filter(is_active=True).select_related('employer', 'category', 'destination')

    # Parse search queries (supports both 'destination' and 'country' URL params)
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    destination_slug = request.GET.get('destination', '').strip() or request.GET.get('country', '').strip()
    job_type = request.GET.get('type', '').strip()

    if search_query:
        jobs_query = jobs_query.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query) |
            Q(employer__company_name__icontains=search_query)
        )

    if category_slug:
        jobs_query = jobs_query.filter(category__slug=category_slug)

    if destination_slug:
        jobs_query = jobs_query.filter(destination__slug=destination_slug)

    if job_type:
        jobs_query = jobs_query.filter(job_type=job_type)

    # Paginate results - 9 per page for grid alignment
    paginator = Paginator(jobs_query, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    destinations = Destination.objects.all()

    context = {
        'jobs': page_obj,
        'categories': categories,
        'destinations': destinations,
        'countries': destinations,  # Fallback for templates using 'countries' loop
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_destination': destination_slug,
        'selected_country': destination_slug,  # Fallback for templates using 'selected_country'
        'selected_type': job_type,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, slug):
    """
    Renders granular view of active job details, highlighting duties, benefits,
    requirements, and contextual buttons indicating if a candidate is ready to apply.
    """
    job = get_object_or_404(Job.objects.select_related('employer', 'category', 'destination'), slug=slug)
    
    # Check states if candidate is authenticated
    has_applied = False
    has_saved = False
    
    if request.user.is_authenticated and request.user.is_candidate:
        profile = getattr(request.user, 'candidate_profile', None)
        if profile:
            has_applied = Application.objects.filter(job=job, candidate=profile).exists()
            has_saved = SavedJob.objects.filter(job=job, candidate=profile).exists()

    # Fetch similar open vacancies
    related_jobs = Job.objects.filter(category=job.category, is_active=True).exclude(id=job.id)[:3]

    context = {
        'job': job,
        'has_applied': has_applied,
        'has_saved': has_saved,
        'related_jobs': related_jobs,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_job_view(request, slug):
    """
    Processes candidate applications. Extracts user profiles, snapshots CV files, 
    and appends a cover letter.
    """
    if not request.user.is_candidate:
        messages.error(request, "Only registered candidates can apply to job listings.")
        return redirect('jobs:job_detail', slug=slug)

    job = get_object_or_404(Job, slug=slug, is_active=True)
    profile = get_object_or_404(CandidateProfile, user=request.user)

    # Check if a CV is loaded in the candidate's profile
    if not profile.resume:
        messages.warning(request, "Please upload a resume in your profile dashboard before applying.")
        return redirect('users:profile')

    # Prevent double submissions
    already_applied = Application.objects.filter(job=job, candidate=profile).exists()
    if already_applied:
        messages.info(request, "You have already submitted an application for this vacancy.")
        return redirect('jobs:job_detail', slug=slug)

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '').strip()
        
        # Save snapshot of current CV file to preserve details for the application
        application = Application.objects.create(
            job=job,
            candidate=profile,
            resume=profile.resume,
            cover_letter=cover_letter,
            status='Applied'
        )
        messages.success(request, f"Your application for '{job.title}' was successfully submitted.")
        return redirect('users:dashboard')

    return render(request, 'jobs/apply_job.html', {'job': job, 'profile': profile})


@login_required
def save_job_view(request, slug):
    """
    Saves or unsaves a job vacancy for a candidate.
    """
    if not request.user.is_candidate:
        messages.error(request, "Only registered candidates can bookmark vacancies.")
        return redirect('jobs:job_detail', slug=slug)

    job = get_object_or_404(Job, slug=slug)
    profile = get_object_or_404(CandidateProfile, user=request.user)

    saved_item, created = SavedJob.objects.get_or_create(candidate=profile, job=job)
    
    if not created:
        saved_item.delete()
        messages.info(request, f"Removed '{job.title}' from your saved jobs.")
    else:
        messages.success(request, f"Successfully saved '{job.title}' to bookmarks.")

    return redirect('jobs:job_detail', slug=slug)


def destinations_list_view(request):
    """
    Renders international destination index.
    """
    destinations = Destination.objects.all()
    return render(request, 'jobs/destinations.html', {'destinations': destinations, 'countries': destinations})


def destination_detail_view(request, slug):
    """
    Renders detailed profile of recruitment opportunities in a specific destination.
    Passes both 'destination' and 'country' keys to support all template tags.
    """
    destination = get_object_or_404(Destination, slug=slug)
    jobs = Job.objects.filter(destination=destination, is_active=True).select_related('employer', 'category')
    return render(request, 'jobs/destination_detail.html', {
        'destination': destination,
        'country': destination,  # Fallback for templates using 'country'
        'jobs': jobs
    })


@login_required
def post_job_view(request):
    """
    Allows validated corporate employers to submit new overseas vacancies.
    """
    if not request.user.is_employer:
        messages.error(request, "Only corporate employers can post job openings.")
        return redirect('users:dashboard')

    profile = get_object_or_404(EmployerProfile, user=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = profile
            job.save()
            messages.success(request, f"Successfully posted vacancy: '{job.title}'.")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Failed to submit vacancy. Please correct the fields below.")
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def update_application_status_view(request, application_id):
    """
    Allows employer owners to change applicant workflow states (Shortlisted, Rejected).
    """
    if not request.user.is_employer:
        messages.error(request, "Access restricted to employers.")
        return redirect('users:dashboard')

    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    application = get_object_or_404(Application, id=application_id, job__employer=employer_profile)

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to: {new_status}.")
        else:
            messages.error(request, "Invalid application status code submitted.")

    return redirect('users:dashboard')


@login_required
def schedule_interview_view(request, application_id):
    """
    Renders scheduling parameters for shortlisted applicants.
    """
    if not request.user.is_employer:
        messages.error(request, "Access restricted to employers.")
        return redirect('users:dashboard')

    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    application = get_object_or_404(Application, id=application_id, job__employer=employer_profile)

    interview, created = Interview.objects.get_or_create(application=application, defaults={'interview_date': timezone.now()})

    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            application.status = 'Interview Scheduled'
            application.save()
            messages.success(request, "Interview scheduling completed and logged.")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Failed to save scheduling data. Review the form.")
    else:
        form = InterviewForm(instance=interview)

    return render(request, 'jobs/schedule_interview.html', {
        'form': form,
        'application': application
    })