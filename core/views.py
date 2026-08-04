import os
import json
import random
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt

from .models import BlogPost, GalleryItem, FAQ, Testimonial, ContactMessage, NewsletterSubscriber
from jobs.models import Job, Destination, Category
from .forms import ContactForm

logger = logging.getLogger(__name__)


def index_view(request):
    """
    Renders the premium, high-converting home page.
    Compiles database statistics, featured vacancies, destination arrays, 
    job categories with placement volumes, testimonials, latest blogs, and FAQs.
    """
    featured_jobs = Job.objects.filter(is_active=True, is_featured=True).select_related('employer', 'destination')[:6]
    latest_jobs = Job.objects.filter(is_active=True).select_related('employer', 'destination')[:6]

    # Fetch all 13 required destinations to show on the Home Page
    destinations = Destination.objects.annotate(job_count=Count('jobs')).all()
    categories = Category.objects.annotate(job_count=Count('jobs')).all()[:8]

    testimonials = Testimonial.objects.filter(is_featured=True)[:5]
    latest_blogs = BlogPost.objects.filter(is_published=True)[:3]
    gallery_items = GalleryItem.objects.all()[:6]
    faqs = FAQ.objects.all()[:5]

    total_candidates = 12450  
    placed_professionals = 8940
    corporate_clients = 320
    countries_reached = 11

    context = {
        'featured_jobs': featured_jobs,
        'latest_jobs': latest_jobs,
        'destinations': destinations,
        'categories': categories,
        'testimonials': testimonials,
        'blogs': latest_blogs,
        'gallery': gallery_items,
        'faqs': faqs,
        'stats': {
            'candidates': total_candidates,
            'placements': placed_professionals,
            'clients': corporate_clients,
            'countries': countries_reached,
        }
    }
    return render(request, 'core/index.html', context)


def about_view(request):
    """
    Corporate overview detail page, outlining company history, executive values, 
    and founder Mirza Khalique Beg's personal strategic vision.
    """
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    return render(request, 'core/about.html', {
        'testimonials': testimonials,
        'founder_name': "Mirza Khalique Beg",
        'founder_phone': "+91 9897920091",
        'office_address': "Office No. T-2, 27-B, 3rd Floor, Khizrabad, Near Lions Hospital, New Delhi – 110025, India"
    })


def services_view(request):
    """
    Dedicated index page detailing recruitment capabilities.
    """
    return render(request, 'core/services.html')


def specialization_view(request):
    """
    Renders the Area of Specialization portfolio page.
    """
    return render(request, 'core/specialization.html')


def gallery_view(request):
    """
    Displays photo portfolio from successful orientation, training, and recruitment drives.
    """
    gallery_items = GalleryItem.objects.all()
    categories = dict(GalleryItem.CATEGORY_CHOICES)
    
    selected_cat = request.GET.get('category', '').strip()
    if selected_cat in categories:
        gallery_items = gallery_items.filter(category=selected_cat)

    context = {
        'gallery': gallery_items,
        'categories': categories,
        'selected_category': selected_cat,
    }
    return render(request, 'core/gallery.html', context)


def blog_list_view(request):
    """
    Paginated blog index showing employment insights and compliance advisories.
    """
    blog_query = BlogPost.objects.filter(is_published=True)
    paginator = Paginator(blog_query, 6) 
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)

    return render(request, 'core/blog_list.html', {'blogs': blogs})


def blog_detail_view(request, slug):
    """
    Renders detailed blog pages alongside related postings and custom SEO tags.
    """
    post = get_object_or_404(BlogPost.objects.select_related('author'), slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:3]
    return render(request, 'core/blog_detail.html', {
        'post': post,
        'related_posts': related_posts
    })


def faq_view(request):
    """
    Detailed Frequently Asked Questions index.
    """
    faqs = FAQ.objects.all()
    return render(request, 'core/faq.html', {'faqs': faqs})


def contact_view(request):
    """
    Processes contact inquiries. Integrates physical addresses, maps, 
    and founder communication links.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been received. Our team will contact you shortly.")
            return redirect('core:contact')
        else:
            messages.error(request, "Failed to submit form. Please verify the information entered.")
    else:
        form = ContactForm()

    context = {
        'form': form,
        'founder_name': "Mirza Khalique Beg",
        'founder_phone': "+91 9897920091",
        'office_address': """Office No. T-2, 27-B, 3rd Floor,
Khizrabad, Near Lions Hospital,
New Delhi – 110025, India""",
    }
    return render(request, 'core/contact.html', context)


def newsletter_subscribe_view(request):
    """
    Handles footer email signups. Supports AJAX or standard POST inquiries.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email address cannot be empty.'}, status=400)
            
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing to our updates.'})
        else:
            return JsonResponse({'status': 'info', 'message': 'You are already registered on our list.'})
            
    return redirect('core:index')


def privacy_policy_view(request):
    """
    Renders standard compliance guidelines for candidate/employer privacy.
    """
    return render(request, 'core/privacy.html')


def terms_view(request):
    """
    Renders official recruitment terms and conditions.
    """
    return render(request, 'core/terms.html')


def sitemap_view(request):
    """
    Generates live XML Sitemap endpoints for search engine spiders.
    """
    domain = f"https://{request.get_host()}"
    
    urls = [
        f"{domain}/",
        f"{domain}/about/",
        f"{domain}/services/",
        f"{domain}/specialization/",
        f"{domain}/jobs/",
        f"{domain}/contact/",
        f"{domain}/privacy/",
        f"{domain}/terms/",
    ]
    
    for job in Job.objects.filter(is_active=True):
        urls.append(f"{domain}/jobs/{job.slug}/")
        
    for dest in Destination.objects.all():
        urls.append(f"{domain}/jobs/destinations/{dest.slug}/")
        
    for blog in BlogPost.objects.filter(is_published=True):
        urls.append(f"{domain}/blog/{blog.slug}/")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url}</loc>\n'
        xml_content += '    <changefreq>weekly</changefreq>\n'
        xml_content += '  </url>\n'
    xml_content += '</urlset>\n'

    return HttpResponse(xml_content, content_type='application/xml')


def custom_404_view(request, exception=None):
    """
    Render global custom 404 page.
    """
    return render(request, 'core/404.html', status=404)


@csrf_exempt
def ai_chat_api(request):
    """
    Processes structured onboarding lead generation data from the frontend State-Machine
    as well as live AI conversational questions.
    Handles both FormData (with resume file uploads) and raw JSON payloads.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    # 1. PARSE REQUEST DATA (Supports both FormData and raw JSON)
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        action = data.get('action', '')
    else:
        # FormData payload (request.POST and request.FILES)
        data = request.POST
        action = data.get('action', '')

    # 2. PROCESS CANDIDATE LEAD SUBMISSION
    if action == "submit_candidate_lead":
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        location = data.get('location', '').strip()
        skills = data.get('skills', '').strip()
        resume_file = request.FILES.get('resume')

        from users.models import CustomUser, CandidateProfile
        
        user_exists = CustomUser.objects.filter(email=email).exists()
        if user_exists:
            user = CustomUser.objects.get(email=email)
            profile, _ = CandidateProfile.objects.get_or_create(user=user)
            if resume_file:
                profile.resume = resume_file
            if location:
                profile.current_location = location
            if skills:
                profile.skills = skills
            profile.save()

            return JsonResponse({
                'status': 'success',
                'response': f"We recognized your email (**{email}**). Your candidate interest in **{location}** has been appended to your profile."
            })

        try:
            username = email.split('@')[0]
            if CustomUser.objects.filter(username=username).exists():
                username = f"{username}{random.randint(10, 99)}"

            user = CustomUser.objects.create(
                email=email,
                username=username,
                first_name=name.split(' ')[0] if name else 'Candidate',
                last_name=name.split(' ')[1] if len(name.split(' ')) > 1 else '',
                phone_number=phone,
                is_candidate=True
            )
            profile, created = CandidateProfile.objects.get_or_create(user=user)
            profile.current_location = location
            profile.skills = skills
            profile.title = skills.split(',')[0] if skills else "Specialist"
            if resume_file:
                profile.resume = resume_file
            profile.save()

            return JsonResponse({
                'status': 'success',
                'response': f"Thank you, **{name}**. We have created a candidate profile for you under username: **{username}**.<br><br>Our talent sourcing team will review your details for active vacancies in **{location}**."
            })
        except Exception as e:
            logger.error(f"Error saving candidate lead: {e}")
            return JsonResponse({
                'status': 'success',
                'response': f"We have noted your details (**{name}** for **{location}**). Our New Delhi operations desk will contact you directly."
            })

    # 3. PROCESS EMPLOYER SOURCING LEAD
    elif action == "submit_employer_lead":
        contact_name = data.get('name', '').strip()
        company_name = data.get('company_name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        needs = data.get('needs', '').strip()

        try:
            ContactMessage.objects.create(
                name=f"{contact_name} ({company_name})" if contact_name else company_name,
                email=email,
                phone=phone,
                subject=f"Employer Sourcing Lead: {company_name}",
                message=f"Contact Person: {contact_name}\nCompany: {company_name}\nSourcing Requirements: {needs}"
            )
            return JsonResponse({
                'status': 'success',
                'response': f"Thank you, **{contact_name or company_name}**. We have registered **{company_name}** into our corporate database.<br><br>An Executive Sourcing Officer and Managing Director **Mirza Khalique Beg** will contact you on **{phone}** or **{email}** within 24 hours to coordinate SLAs."
            })
        except Exception as e:
            logger.error(f"Error saving employer lead: {e}")
            return JsonResponse({
                'status': 'success',
                'response': "We have registered your corporate requirements. Our New Delhi corporate desk will contact you shortly."
            })

    # 4. LIVE CONVERSATIONAL AI CHAT (Gemini / OpenAI API + Intelligent Rule-Based Fallback)
    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'status': 'error', 'response': "Please type a message to start."}, status=400)

    system_prompt = (
        "You are the 24/7 AI Sourcing Assistant for 'Elevate Workforce', an international recruitment "
        "and manpower agency headquartered in New Delhi, India, with regional offices in Jeddah, Dammam (KSA), and Lucknow. "
        "Managing Director: Mirza Khalique Beg (+91 9897920091, elevateworkforce21@gmail.com). "
        "Key operational markets: UAE, KSA, Qatar, Kuwait, Bahrain, Romania, Croatia, Poland. "
        "Key trades: Welders, HVAC, Electrical, Civil Engineers, Healthcare, Hospitality, Oil & Gas. "
        "Provide clear, professional, and helpful answers in 2-3 sentences."
    )

    # A. Gemini API Integration
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser Question: {user_message}"}]}]
            }
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            if res.status_code == 200:
                res_data = res.json()
                bot_reply = res_data['candidates'][0]['content']['parts'][0]['text']
                return JsonResponse({'status': 'success', 'response': bot_reply})
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")

    # B. OpenAI API Integration Fallback
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            import requests
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openai_api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 150
            }
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                res_data = res.json()
                bot_reply = res_data['choices'][0]['message']['content']
                return JsonResponse({'status': 'success', 'response': bot_reply})
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")

    # C. Rule-Based Fallback Logic
    msg_lower = user_message.lower()
    if any(k in msg_lower for k in ['job', 'apply', 'work', 'vacancy', 'openings', 'candidate', 'resume', 'cv']):
        response_text = (
            "We are actively recruiting for multiple positions in "
            "<strong>Dubai, Saudi Arabia, Qatar, Romania, and Croatia</strong>. "
            "To apply, please register your candidate profile or view our active jobs directory."
        )
    elif any(k in msg_lower for k in ['recruit', 'employer', 'client', 'hire', 'hiring', 'manpower', 'sourcing']):
        response_text = (
            "Elevate Workforce provides streamlined, compliant recruitment solutions for international employers. "
            "Submit your requirements or contact Director <strong>Mirza Khalique Beg</strong> at +91 9897920091."
        )
    elif any(k in msg_lower for k in ['address', 'office', 'location', 'where', 'delhi']):
        response_text = (
            "Our head office is located at Office No. T-2, 27-B, 3rd Floor, Khizrabad, Near Lions Hospital, New Delhi - 110025, India."
        )
    elif any(k in msg_lower for k in ['owner', 'director', 'mirza', 'khalique', 'beg']):
        response_text = (
            "Our Director is <strong>Mirza Khalique Beg</strong>. You can reach him directly via phone or WhatsApp at +91 9897920091."
        )
    elif any(k in msg_lower for k in ['visa', 'gamca', 'passport', 'process']):
        response_text = (
            "We coordinate complete visa processing, GAMCA medical setups, and embassy endorsements directly with MEA and target country consulates."
        )
    else:
        response_text = "Hello! Thank you for contacting Elevate Workforce. How can I assist you with international recruitment or job vacancies today?"

    return JsonResponse({'status': 'success', 'response': response_text})

def seed_data_view(request):
    """
    1-Click Auto Seed View: Creates all 13 Destinations, 8 Categories, 
    Sample Corporate Employer, and Active Sample Jobs directly in DB.
    """
    from jobs.models import Destination, Category, Job
    from users.models import CustomUser, EmployerProfile

    # 1. All 13 Sourcing Destinations
    destinations_data = [
        ("Dubai", "dubai", "AE", "Executive and skilled manpower sourcing for Dubai, UAE."),
        ("Saudi Arabia", "saudi-arabia", "SA", "Comprehensive recruitment solutions across Saudi Arabia."),
        ("Riyadh", "riyadh", "SA", "Corporate and technical staffing for Riyadh, Saudi Arabia."),
        ("Jeddah", "jeddah", "SA", "Workforce recruitment for Jeddah region, Saudi Arabia."),
        ("Dammam", "dammam", "SA", "Industrial manpower sourcing for Dammam region, Saudi Arabia."),
        ("Qatar", "qatar", "QA", "Overseas recruitment and manpower supply for Qatar."),
        ("Kuwait", "kuwait", "KW", "Manpower recruitment and staffing for Kuwait."),
        ("Poland", "poland", "PL", "Recruitment and work permit sourcing for Poland."),
        ("Romania", "romania", "RO", "EU work permit and industrial manpower for Romania."),
        ("Malta", "malta", "MT", "European work permit and staffing for Malta."),
        ("Serbia", "serbia", "RS", "European construction and technical sourcing for Serbia."),
        ("Russia", "russia", "RU", "Technical and industrial sourcing for Russia."),
        ("Turkey", "turkey", "TR", "Workforce solutions and sourcing for Turkey.")
    ]

    dest_objs = {}
    for name, slug, flag, desc in destinations_data:
        obj, _ = Destination.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'flag_code': flag, 'description': desc}
        )
        if not obj.description:
            obj.description = desc
            obj.save()
        dest_objs[slug] = obj

    # 2. Industry Sectors
    categories_data = [
        ("Oil & Gas", "oil-gas", "fa-oil-well"),
        ("Construction", "construction", "fa-helmet-safety"),
        ("Mechanical", "mechanical", "fa-screwdriver-wrench"),
        ("Civil", "civil", "fa-building"),
        ("Electrical", "electrical", "fa-bolt"),
        ("Hospitality", "hospitality", "fa-bell-concierge"),
        ("Healthcare", "healthcare", "fa-user-nurse"),
        ("IT & Technology", "it-technology", "fa-laptop-code"),
    ]

    cat_objs = {}
    for name, slug, icon in categories_data:
        obj, _ = Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'icon_class': icon, 'description': f"{name} sector."}
        )
        cat_objs[slug] = obj

    # 3. Sample Corporate Employer Profile
    emp_user, _ = CustomUser.objects.get_or_create(
        email="corporate@elevateworkforce.com",
        defaults={
            'username': 'elevate_corporate',
            'first_name': 'Elevate',
            'last_name': 'Employer',
            'is_employer': True
        }
    )
    emp_profile, _ = EmployerProfile.objects.get_or_create(
        user=emp_user,
        defaults={
            'company_name': 'Elevate Global Partners',
            'is_verified_employer': True,
            'website': 'https://elevateworkforce.com'
        }
    )

    # 4. Active Vacancies Jobs
    sample_jobs = [
        ("Senior Structural Welder", "senior-structural-welder", "oil-gas", "dubai", "3,500 - 5,000 AED / Month", "5+ Years"),
        ("HVAC Maintenance Technician", "hvac-maintenance-technician", "mechanical", "saudi-arabia", "3,000 - 4,200 SAR / Month", "3+ Years"),
        ("Civil Site Engineer", "civil-site-engineer", "civil", "qatar", "6,000 - 8,500 QAR / Month", "4+ Years"),
        ("Electrical Panel Builder", "electrical-panel-builder", "electrical", "dammam", "2,800 - 3,800 SAR / Month", "3+ Years"),
        ("Hotel Operations Supervisor", "hotel-operations-supervisor", "hospitality", "poland", "1,200 - 1,600 EUR / Month", "2+ Years"),
        ("Warehouse Logistics Handler", "warehouse-logistics-handler", "construction", "romania", "1,000 - 1,400 EUR / Month", "1+ Years"),
    ]

    for title, slug, cat_slug, dest_slug, salary, exp in sample_jobs:
        Job.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title,
                'employer': emp_profile,
                'category': cat_objs.get(cat_slug),
                'destination': dest_objs.get(dest_slug),
                'job_type': 'Full-time',
                'salary_range': salary,
                'experience_required': exp,
                'vacancies': 5,
                'description': f"Seeking experienced {title} for international deployment.",
                'requirements': "Relevant certifications, valid passport, and technical skills.",
                'is_active': True,
                'is_featured': True
            }
        )

    messages.success(request, "🎉 Success! Created Destinations, Categories, and Sample Active Jobs in Database.")
    return redirect('jobs:job_list')