from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # About
    path("about/", views.about, name="about"),

    # Leadership
    path("leadership/", views.leadership_view, name="leadership"),

    # Ministries
    path("ministries/", views.ministries_view, name="ministries"),

    # Sermons
    path("sermons/", views.sermons_view, name="sermons"),
    path("sermons/<slug:slug>/", views.sermon_detail, name="sermon_detail"),

    # Devotionals
    path("devotionals/", views.devotionals_view, name="devotionals"),
    path("devotionals/<slug:slug>/", views.devotional_detail, name="devotional_detail"),

    # Events
    path("events/", views.events_view, name="events"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),

    # Gallery
    path("gallery/", views.gallery_view, name="gallery"),

    # Testimonies
    path("testimonies/", views.testimonies_view, name="testimonies"),
    path("testimonies/<slug:slug>/", views.testimony_detail, name="testimony_detail"),

    # Give
    path("give/", views.give_view, name="give"),

    # Contact
    path("contact/", views.contact_view, name="contact"),

    # Prayer Request
    path("prayer-request/", views.prayer_request_view, name="prayer_request"),

    # First Visit
    path("first-visit/", views.first_visit_view, name="first_visit"),

    # Search
    path("search/", views.search_results, name="search_results"),

    # Newsletter Subscription (POST-only, handles redirect)
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    # Dashboard
path("dashboard/", views.dashboard, name="dashboard"),

# Dashboard - Devotionals
path(
    "dashboard/devotionals/add/",
    views.dashboard_add_devotional,
    name="dashboard_add_devotional",
),
path(
    "dashboard/devotionals/<int:pk>/edit/",
    views.dashboard_edit_devotional,
    name="dashboard_edit_devotional",
),
path(
    "dashboard/devotionals/<int:pk>/delete/",
    views.dashboard_delete_devotional,
    name="dashboard_delete_devotional",
),

# Dashboard - Leadership
path(
    "dashboard/leadership/add/",
    views.dashboard_add_leadership,
    name="dashboard_add_leadership",
),
path(
    "dashboard/leadership/<int:pk>/edit/",
    views.dashboard_edit_leadership,
    name="dashboard_edit_leadership",
),
path(
    "dashboard/leadership/<int:pk>/delete/",
    views.dashboard_delete_leadership,
    name="dashboard_delete_leadership",
),

# Dashboard - Events
path(
    "dashboard/events/add/",
    views.dashboard_add_event,
    name="dashboard_add_event",
),
path(
    "dashboard/events/<int:pk>/edit/",
    views.dashboard_edit_event,
    name="dashboard_edit_event",
),
path(
    "dashboard/events/<int:pk>/delete/",
    views.dashboard_delete_event,
    name="dashboard_delete_event",
),
]