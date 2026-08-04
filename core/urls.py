from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('specialization/', views.specialization_view, name='specialization'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    path('api/ai-chat/', views.ai_chat_api, name='ai_chat_api'),
    
    # 🚀 1-CLICK AUTO SEED ROUTE
    path('seed/', views.seed_data_view, name='seed_data'),

    path('gallery/', views.gallery_view, name='gallery'),
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy'),
    path('terms-and-conditions/', views.terms_view, name='terms'),
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
]