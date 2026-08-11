from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.http import Http404
from django.contrib.auth.decorators import login_required
import requests

IMGBB_API_KEY = "b15da317474447e69e6859a9ad6ba545"
from .models import (
    ChurchSettings,
    HomepageSettings,
    HeroSlide,
    Announcement,
    ServiceSchedule,
    Leadership,
    Ministry,
    SermonCategory,
    Sermon,
    Devotional,
    Event,
    GalleryAlbum,
    GalleryImage,
    Testimony,
    PrayerRequest,
    ContactMessage,
    GivingInformation,
    NewsletterSubscriber,
)
from .forms import (
    ContactForm,
    DevotionalForm,
    PrayerRequestForm,
    FirstVisitForm,
    NewsletterForm,
    SearchForm,
)


# ---------- Helper: get global context (for all views) ----------
def get_global_context(request):
    """Return context data that is common to all pages."""
    try:
        church_settings = ChurchSettings.load()
    except ChurchSettings.DoesNotExist:
        church_settings = None
    return {
        'church_settings': church_settings,
        'newsletter_form': NewsletterForm(),
    }


# ---------- Home View ----------
def home(request):
    context = get_global_context(request)

    # Load Homepage Settings
    try:
        homepage_settings = HomepageSettings.load()
    except HomepageSettings.DoesNotExist:
        homepage_settings = None
    context['homepage_settings'] = homepage_settings

    # Hero Slides (active only)
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by('display_order')
    context['hero_slides'] = hero_slides

    # Announcements (active, not expired)
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        Q(display_until__isnull=True) | Q(display_until__gte=now)
    ).order_by('display_order')
    context['announcements'] = announcements

    # Service Schedules
    schedules = ServiceSchedule.objects.filter(is_active=True).order_by('day', 'start_time')
    context['service_schedules'] = schedules

    # Sermons: latest 5 published, with category prefetched
    latest_sermons = Sermon.objects.filter(published=True).select_related('category').order_by('-date_preached')[:5]
    context['latest_sermons'] = latest_sermons

    # Featured Sermon (from homepage settings)
    if homepage_settings and homepage_settings.featured_sermon:
        featured_sermon = homepage_settings.featured_sermon
        context['featured_sermon'] = featured_sermon

    # Devotionals: latest 5 published
    latest_devotionals = Devotional.objects.filter(published=True).order_by('-created_at')[:5]
    context['latest_devotionals'] = latest_devotionals

    # Featured Devotional
    if homepage_settings and homepage_settings.featured_devotional:
        context['featured_devotional'] = homepage_settings.featured_devotional

    # Events: upcoming only (start_date >= now) and published, ordered by start_date
    upcoming_events = Event.objects.filter(
        published=True,
        start_date__gte=now
    ).order_by('start_date')[:5]
    context['upcoming_events'] = upcoming_events

    # Featured Event
    if homepage_settings and homepage_settings.featured_event:
        context['featured_event'] = homepage_settings.featured_event

    # Leadership (show_on_homepage=True)
    leadership_home = Leadership.objects.filter(show_on_homepage=True).order_by('display_order')[:5]
    context['leadership_home'] = leadership_home

    # Ministries (all, ordered)
    ministries = Ministry.objects.all().order_by('display_order', 'name')
    context['ministries'] = ministries

    # Gallery: latest album with its cover and some images
    latest_album = GalleryAlbum.objects.filter(published=True).order_by('-created_at').first()
    if latest_album:
        album_images = latest_album.images.all().order_by('display_order')[:6]  # prefetch images
        context['latest_album'] = latest_album
        context['album_images'] = album_images

    # Testimonies: approved, featured first, then latest
    latest_testimonies = Testimony.objects.filter(approved=True).order_by('-featured', '-published_date')[:5]
    context['latest_testimonies'] = latest_testimonies

    # Featured Testimony
    if homepage_settings and homepage_settings.featured_testimony:
        context['featured_testimony'] = homepage_settings.featured_testimony

    return render(request, 'home.html', context)


# ---------- About View ----------
def about(request):
    context = get_global_context(request)
    try:
        church_settings = ChurchSettings.load()
    except ChurchSettings.DoesNotExist:
        church_settings = None
    context['church_settings'] = church_settings

    # Leadership (all, ordered)
    leadership = Leadership.objects.all().order_by('display_order', 'name')
    context['leadership'] = leadership

    return render(request, 'about.html', context)


# ---------- Leadership View ----------
def leadership_view(request):
    context = get_global_context(request)
    leadership = Leadership.objects.all().order_by('display_order', 'name')
    context['leadership'] = leadership
    return render(request, 'leadership.html', context)


# ---------- Ministries View ----------
def ministries_view(request):
    context = get_global_context(request)
    ministries = Ministry.objects.all().order_by('display_order', 'name')
    context['ministries'] = ministries
    return render(request, 'ministries.html', context)


# ---------- Sermons List View ----------
def sermons_view(request):
    context = get_global_context(request)

    # Base queryset: published sermons, select category
    sermons_qs = Sermon.objects.filter(published=True).select_related('category')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        sermons_qs = sermons_qs.filter(category__slug=category_slug)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        sermons_qs = sermons_qs.filter(
            Q(title__icontains=search_query) |
            Q(speaker__icontains=search_query) |
            Q(bible_reference__icontains=search_query) |
            Q(summary__icontains=search_query)
        )

    # Order by date preached descending
    sermons_qs = sermons_qs.order_by('-date_preached')

    # Pagination
    paginator = Paginator(sermons_qs, 12)
    page = request.GET.get('page')
    try:
        sermons = paginator.page(page)
    except PageNotAnInteger:
        sermons = paginator.page(1)
    except EmptyPage:
        sermons = paginator.page(paginator.num_pages)

    # Categories for filter sidebar
    categories = SermonCategory.objects.all().order_by('title')

    context.update({
        'sermons': sermons,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
    })
    return render(request, 'sermons.html', context)


# ---------- Sermon Detail View ----------
def sermon_detail(request, slug):
    context = get_global_context(request)
    sermon = get_object_or_404(Sermon, slug=slug, published=True)

    # Increment view count
    sermon.views += 1
    sermon.save(update_fields=['views'])

    # Related sermons: same category, exclude current, limit 5
    related = Sermon.objects.filter(
        category=sermon.category,
        published=True
    ).exclude(id=sermon.id).order_by('-date_preached')[:5]

    context.update({
        'sermon': sermon,
        'related_sermons': related,
    })
    return render(request, 'sermon_detail.html', context)


# ---------- Devotionals List View ----------
def devotionals_view(request):
    context = get_global_context(request)
    devotionals_qs = Devotional.objects.filter(published=True)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        devotionals_qs = devotionals_qs.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(scripture__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    devotionals_qs = devotionals_qs.order_by('-created_at')
    paginator = Paginator(devotionals_qs, 10)
    page = request.GET.get('page')
    try:
        devotionals = paginator.page(page)
    except PageNotAnInteger:
        devotionals = paginator.page(1)
    except EmptyPage:
        devotionals = paginator.page(paginator.num_pages)

    context.update({
        'devotionals': devotionals,
        'search_query': search_query,
    })
    return render(request, 'devotionals.html', context)


# ---------- Devotional Detail View ----------
def devotional_detail(request, slug):
    context = get_global_context(request)
    devotional = get_object_or_404(Devotional, slug=slug, published=True)

    devotional.views += 1
    devotional.save(update_fields=['views'])

    # Related: same author or similar, exclude current
    related = Devotional.objects.filter(
        published=True
    ).exclude(id=devotional.id).order_by('-created_at')[:5]

    context.update({
        'devotional': devotional,
        'related_devotionals': related,
    })
    return render(request, 'devotional_detail.html', context)


# ---------- Events List View ----------
def events_view(request):
    context = get_global_context(request)
    now = timezone.now()

    # Upcoming events (start_date >= now)
    upcoming = Event.objects.filter(
        published=True,
        start_date__gte=now
    ).order_by('start_date')

    # Past events (start_date < now)
    past = Event.objects.filter(
        published=True,
        start_date__lt=now
    ).order_by('-start_date')

    # Paginate both separately or combine? We'll separate.
    paginator_upcoming = Paginator(upcoming, 10)
    page_upcoming = request.GET.get('upcoming_page')
    try:
        upcoming_paginated = paginator_upcoming.page(page_upcoming)
    except PageNotAnInteger:
        upcoming_paginated = paginator_upcoming.page(1)
    except EmptyPage:
        upcoming_paginated = paginator_upcoming.page(paginator_upcoming.num_pages)

    paginator_past = Paginator(past, 10)
    page_past = request.GET.get('past_page')
    try:
        past_paginated = paginator_past.page(page_past)
    except PageNotAnInteger:
        past_paginated = paginator_past.page(1)
    except EmptyPage:
        past_paginated = paginator_past.page(paginator_past.num_pages)

    context.update({
        'upcoming_events': upcoming_paginated,
        'past_events': past_paginated,
    })
    return render(request, 'events.html', context)


# ---------- Event Detail View ----------
def event_detail(request, slug):
    context = get_global_context(request)
    event = get_object_or_404(Event, slug=slug, published=True)

    # Related events (same type or upcoming)
    related = Event.objects.filter(
        published=True,
        event_type=event.event_type
    ).exclude(id=event.id).order_by('start_date')[:5]

    context.update({
        'event': event,
        'related_events': related,
    })
    return render(request, 'event_detail.html', context)


# ---------- Gallery View ----------
def gallery_view(request):
    context = get_global_context(request)
    albums = GalleryAlbum.objects.filter(published=True).order_by('display_order', '-created_at')

    # For each album, prefetch images for cover? Not needed if cover is used.
    # We'll paginate albums.
    paginator = Paginator(albums, 9)
    page = request.GET.get('page')
    try:
        albums_paginated = paginator.page(page)
    except PageNotAnInteger:
        albums_paginated = paginator.page(1)
    except EmptyPage:
        albums_paginated = paginator.page(paginator.num_pages)

    context['albums'] = albums_paginated
    return render(request, 'gallery.html', context)


# ---------- Testimonies View ----------
def testimonies_view(request):
    context = get_global_context(request)
    testimonies_qs = Testimony.objects.filter(approved=True).order_by('-featured', '-published_date')

    # Search
    search_query = request.GET.get('q')
    if search_query:
        testimonies_qs = testimonies_qs.filter(
            Q(full_name__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(story__icontains=search_query)
        )

    paginator = Paginator(testimonies_qs, 10)
    page = request.GET.get('page')
    try:
        testimonies = paginator.page(page)
    except PageNotAnInteger:
        testimonies = paginator.page(1)
    except EmptyPage:
        testimonies = paginator.page(paginator.num_pages)

    context.update({
        'testimonies': testimonies,
        'search_query': search_query,
    })
    return render(request, 'testimonies.html', context)


# ---------- Testimony Detail View ----------
def testimony_detail(request, slug):
    context = get_global_context(request)
    testimony = get_object_or_404(Testimony, slug=slug, approved=True)

    # Related
    related = Testimony.objects.filter(approved=True).exclude(id=testimony.id).order_by('-published_date')[:5]

    context.update({
        'testimony': testimony,
        'related_testimonies': related,
    })
    return render(request, 'testimony_detail.html', context)


# ---------- Give View ----------
def give_view(request):
    context = get_global_context(request)

    # Giving information
    giving_info = GivingInformation.objects.all().order_by('display_order')
    context['giving_info'] = giving_info

    # Church settings (already loaded)
    return render(request, 'give.html', context)


# ---------- Contact View ----------
def contact_view(request):
    context = get_global_context(request)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            # Any additional logic? None.
            contact.save()
            messages.success(request, "Your message has been sent successfully. We'll get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    context['form'] = form
    return render(request, 'contact.html', context)


# ---------- Prayer Request View ----------
def prayer_request_view(request):
    context = get_global_context(request)

    if request.method == 'POST':
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.save()
            messages.success(request, "Your prayer request has been submitted. We are praying with you.")
            return redirect('prayer_request')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PrayerRequestForm()

    context['form'] = form
    return render(request, 'prayer_request.html', context)


# ---------- First Visit View ----------
def first_visit_view(request):
    context = get_global_context(request)

    if request.method == 'POST':
        form = FirstVisitForm(request.POST)
        if form.is_valid():
            # Save? The form is not a ModelForm, so we need to save manually if we have a model.
            # But FirstVisitForm is a normal Form, not ModelForm. There is no FirstVisit model.
            # The instruction says "Support planned_date, number_of_guests, children, notes" but no model.
            # We'll just show success message and redirect.
            # In real project, we might store in session or create a model. But since no model, we can just show success.
            messages.success(request, "Thank you! We look forward to welcoming you. We'll be in touch.")
            return redirect('first_visit')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FirstVisitForm()

    context['form'] = form
    return render(request, 'first_visit.html', context)


# ---------- Search Results View ----------
def search_results(request):
    context = get_global_context(request)
    form = SearchForm(request.GET)
    query = ''
    results = {
        'sermons': [],
        'devotionals': [],
        'events': [],
        'testimonies': [],
        'ministries': [],
    }
    if form.is_valid():
        query = form.cleaned_data.get('q', '').strip()
        if query:
            # Search across models
            sermons = Sermon.objects.filter(
                Q(title__icontains=query) |
                Q(speaker__icontains=query) |
                Q(bible_reference__icontains=query) |
                Q(summary__icontains=query) |
                Q(content__icontains=query),
                published=True
            ).select_related('category')[:10]
            devotionals = Devotional.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(scripture__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query),
                published=True
            )[:10]
            events = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(venue__icontains=query),
                published=True
            ).order_by('start_date')[:10]
            testimonies = Testimony.objects.filter(
                Q(full_name__icontains=query) |
                Q(title__icontains=query) |
                Q(story__icontains=query),
                approved=True
            )[:10]
            ministries = Ministry.objects.filter(
                Q(name__icontains=query) |
                Q(leader__icontains=query) |
                Q(description__icontains=query)
            )[:10]

            results = {
                'sermons': sermons,
                'devotionals': devotionals,
                'events': events,
                'testimonies': testimonies,
                'ministries': ministries,
            }

    context['form'] = form
    context['query'] = query
    context['results'] = results
    return render(request, 'search_results.html', context)


# ---------- Newsletter Subscribe (AJAX or separate? We'll handle via POST) ----------
def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                subscriber = form.save(commit=False)
                subscriber.save()
                messages.success(request, "You have been subscribed to our newsletter.")
            except Exception as e:
                # Possibly duplicate error already handled in form clean
                messages.error(request, "Subscription failed. Please try again.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        # Redirect back to the page they came from
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        return redirect('home')
# ============================================================
# DASHBOARD
# ============================================================

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404


# ---------- Dashboard Home ----------

@login_required
def dashboard(request):
    context = {
        # Main content
        "devotionals": Devotional.objects.all().order_by("-created_at")[:10],
        "leadership": Leadership.objects.all().order_by("display_order", "name")[:10],
        "events": Event.objects.all().order_by("-start_date")[:10],

        # Other content
        "sermons": Sermon.objects.all().order_by("-date_preached")[:5],
        "ministries": Ministry.objects.all().order_by("display_order", "name")[:5],
        "testimonies": Testimony.objects.all().order_by("-published_date")[:5],

        # Messages / requests
        "prayer_requests": PrayerRequest.objects.all().order_by("-submitted_date")[:5],
        "contact_messages": ContactMessage.objects.all().order_by("-submitted_date")[:5],
        "newsletter_subscribers": NewsletterSubscriber.objects.all().order_by("-subscribed_date")[:5],

        # Statistics
        "devotional_count": Devotional.objects.count(),
        "leadership_count": Leadership.objects.count(),
        "event_count": Event.objects.count(),
        "sermon_count": Sermon.objects.count(),
        "ministry_count": Ministry.objects.count(),
        "testimony_count": Testimony.objects.count(),
        "prayer_count": PrayerRequest.objects.count(),
        "message_count": ContactMessage.objects.count(),
        "subscriber_count": NewsletterSubscriber.objects.count(),
    }

    return render(request, "dashboard.html", context)


# ============================================================
# DEVOTIONALS
# ============================================================

@login_required
def dashboard_add_devotional(request):

    if request.method == "POST":
        form = DevotionalForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Devotional published successfully."
            )
            return redirect("core:dashboard")

    else:
        form = DevotionalForm()

    return render(
        request,
        "dashboard/devotional_form.html",
        {
            "form": form,
        }
    )


@login_required
def dashboard_edit_devotional(request, pk):

    devotional = get_object_or_404(Devotional, pk=pk)

    if request.method == "POST":

        devotional.title = request.POST.get("title", "").strip()
        devotional.scripture = request.POST.get("scripture", "").strip()
        devotional.author = request.POST.get("author", "").strip()
        devotional.excerpt = request.POST.get("excerpt", "").strip()
        devotional.content = request.POST.get("content", "").strip()

        devotional.published = request.POST.get("published") == "on"
        devotional.featured = request.POST.get("featured") == "on"

        if request.FILES.get("featured_image"):
            devotional.featured_image = request.FILES.get("featured_image")

        devotional.save()

        messages.success(request, "Devotional updated successfully.")
        return redirect("core:dashboard")

    return render(
        request,
        "dashboard/devotional_form.html",
        {"devotional": devotional}
    )


@login_required
def dashboard_delete_devotional(request, pk):

    devotional = get_object_or_404(Devotional, pk=pk)

    if request.method == "POST":
        devotional.delete()
        messages.success(request, "Devotional deleted successfully.")

    return redirect("core:dashboard")


# ============================================================
# LEADERSHIP
# ============================================================

@login_required
def dashboard_add_leadership(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        position = request.POST.get("position", "").strip()
        biography = request.POST.get("biography", "").strip()
        quote = request.POST.get("quote", "").strip()

        display_order = request.POST.get("display_order") or 0
        show_on_homepage = request.POST.get("show_on_homepage") == "on"

        photo = request.FILES.get("photo")

        if not name:
            messages.error(request, "Leader name is required.")
            return redirect("core:dashboard_add_leadership")

        leader = Leadership(
            name=name,
            position=position,
            biography=biography,
            quote=quote,
            display_order=display_order,
            show_on_homepage=show_on_homepage,
            photo=photo,
        )

        leader.save()

        messages.success(request, "Leader added successfully.")
        return redirect("core:dashboard")

    return render(request, "dashboard/leadership_form.html")


@login_required
def dashboard_edit_leadership(request, pk):

    leader = get_object_or_404(Leadership, pk=pk)

    if request.method == "POST":

        leader.name = request.POST.get("name", "").strip()
        leader.position = request.POST.get("position", "").strip()
        leader.biography = request.POST.get("biography", "").strip()
        leader.quote = request.POST.get("quote", "").strip()

        leader.display_order = request.POST.get("display_order") or 0
        leader.show_on_homepage = request.POST.get("show_on_homepage") == "on"

        if request.FILES.get("photo"):
            leader.photo = request.FILES.get("photo")

        leader.save()

        messages.success(request, "Leader updated successfully.")
        return redirect("core:dashboard")

    return render(
        request,
        "dashboard/leadership_form.html",
        {"leader": leader}
    )


@login_required
def dashboard_delete_leadership(request, pk):

    leader = get_object_or_404(Leadership, pk=pk)

    if request.method == "POST":
        leader.delete()
        messages.success(request, "Leader deleted successfully.")

    return redirect("core:dashboard")


# ============================================================
# EVENTS
# ============================================================

@login_required
def dashboard_add_event(request):

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        event_type = request.POST.get("event_type", "service")
        description = request.POST.get("description", "").strip()
        venue = request.POST.get("venue", "").strip()

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        registration_link = request.POST.get("registration_link", "").strip()
        google_maps_link = request.POST.get("google_maps_link", "").strip()

        featured = request.POST.get("featured") == "on"
        published = request.POST.get("published") == "on"

        banner = request.FILES.get("banner")

        if not title:
            messages.error(request, "Event title is required.")
            return redirect("core:dashboard_add_event")

        if not start_date:
            messages.error(request, "Event start date is required.")
            return redirect("core:dashboard_add_event")

        event = Event(
            title=title,
            event_type=event_type,
            description=description,
            venue=venue,
            start_date=start_date,
            end_date=end_date or None,
            registration_link=registration_link,
            google_maps_link=google_maps_link,
            featured=featured,
            published=published,
            banner=banner,
        )

        event.save()

        messages.success(request, "Event added successfully.")
        return redirect("core:dashboard")

    return render(request, "dashboard/event_form.html")


@login_required
def dashboard_edit_event(request, pk):

    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":

        event.title = request.POST.get("title", "").strip()
        event.event_type = request.POST.get("event_type", "service")
        event.description = request.POST.get("description", "").strip()
        event.venue = request.POST.get("venue", "").strip()

        event.start_date = request.POST.get("start_date")
        event.end_date = request.POST.get("end_date") or None

        event.registration_link = request.POST.get(
            "registration_link", ""
        ).strip()

        event.google_maps_link = request.POST.get(
            "google_maps_link", ""
        ).strip()

        event.featured = request.POST.get("featured") == "on"
        event.published = request.POST.get("published") == "on"

        if request.FILES.get("banner"):
            event.banner = request.FILES.get("banner")

        event.save()

        messages.success(request, "Event updated successfully.")
        return redirect("core:dashboard")

    return render(
        request,
        "dashboard/event_form.html",
        {"event": event}
    )


@login_required
def dashboard_delete_event(request, pk):

    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")

    return redirect("core:dashboard")