from django.utils import timezone
from django.db.models import Q

from .models import (
    ChurchSettings,
    HomepageSettings,
    SocialLink,
    ServiceSchedule,
    Announcement,
)
from .forms import NewsletterForm


def global_context(request):
    """
    Context processor that injects global data into every template.
    All views benefit from these variables without needing to pass them manually.
    """
    context = {}

    # Church Settings - Singleton
    try:
        church_settings = ChurchSettings.load()
    except ChurchSettings.DoesNotExist:
        church_settings = None
    context['church_settings'] = church_settings

    # Homepage Settings - Singleton
    try:
        homepage_settings = HomepageSettings.load()
    except HomepageSettings.DoesNotExist:
        homepage_settings = None
    context['homepage_settings'] = homepage_settings

    # Social Links - only active ones, ordered by display_order
    social_links = SocialLink.objects.filter(is_active=True).order_by('display_order')
    context['social_links'] = social_links

    # Service Schedule - active only, ordered by day and time
    service_schedule = ServiceSchedule.objects.filter(is_active=True).order_by('day', 'start_time')
    context['service_schedule'] = service_schedule

    # Announcements - active and not expired, ordered by display_order
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        Q(display_until__isnull=True) | Q(display_until__gte=now)
    ).order_by('display_order')
    context['announcements'] = announcements

    # Current year for footer copyright
    context['current_year'] = timezone.now().year

    # Newsletter form - available globally for any page that wants to show a subscription form
    context['newsletter_form'] = NewsletterForm()

    # Additional convenience: if church settings exist, expose common fields directly
    if church_settings:
        context['church_name'] = church_settings.church_name
        context['church_logo'] = church_settings.logo
        context['church_favicon'] = church_settings.favicon
        context['church_address'] = church_settings.address
        context['church_phone'] = church_settings.phone
        context['church_email'] = church_settings.email
        context['footer_copyright'] = church_settings.copyright_text
        # Livestream info
        context['livestream_enabled'] = church_settings.livestream_enabled
        context['youtube_live_url'] = church_settings.youtube_live_url
    else:
        # Safe defaults
        context['church_name'] = None
        context['church_logo'] = None
        context['church_favicon'] = None
        context['church_address'] = None
        context['church_phone'] = None
        context['church_email'] = None
        context['footer_copyright'] = None
        context['livestream_enabled'] = False
        context['youtube_live_url'] = None

    return context