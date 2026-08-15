from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models

from .models import (
    ChurchSettings,
    HomepageSettings,
    GalleryImage,
    GalleryAlbum,
    HeroSlide,
    Announcement,
    ServiceSchedule,
    SocialLink,
    Leadership,
    Ministry,
    SermonCategory,
    Sermon,
    Devotional,
    Event,
    Testimony,
    PrayerRequest,
    ContactMessage,
    GivingInformation,
    NewsletterSubscriber,
)


# ---------- Admin Site Customization ----------
admin.site.site_header = _("Embassy of God's Word Ministry Administration")
admin.site.site_title = _("Embassy of God's Word Ministry")
admin.site.index_title = _("Welcome to the Church Admin Dashboard")


# ---------- Helper Mixin for Image Preview ----------
class ImagePreviewMixin:
    """Adds image preview methods for models with ImageFields."""

    def preview_image(self, obj, field_name="image", width=80, height=80):
        """Generic image preview."""
        image = getattr(obj, field_name, None)
        if image:
            return format_html(
                '<img src="{}" style="width: {}px; height: {}px; object-fit: cover; border-radius: 4px;" />',
                image.url, width, height
            )
        return format_html(
            '<span style="color: #999; font-size: 12px;">No image</span>'
        )

    preview_image.short_description = _("Preview")


# ---------- Singleton Admin ----------
class SingletonAdmin(admin.ModelAdmin):
    """Admin for singleton models (only one instance)."""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------- Church Settings ----------
@admin.register(ChurchSettings)
class ChurchSettingsAdmin(SingletonAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General Information"), {
            "fields": (
                "church_name", "short_name", "tagline", "mission", "vision", "motto",
            )
        }),
        (_("Contact & Location"), {
            "fields": (
                "address", "email", "phone", "alternate_phone", "google_maps_embed",
            )
        }),
        (_("Branding & Media"), {
            "fields": (
                "logo", "favicon", "hero_default_image",
            )
        }),
        (_("Live Stream"), {
            "fields": (
                "youtube_live_url", "livestream_enabled",
            )
        }),
        (_("Service & Office"), {
            "fields": (
                "service_times_text", "office_hours",
            )
        }),
        (_("Social Links"), {
            "fields": (
                "facebook", "instagram", "youtube", "tiktok", "whatsapp", "telegram",
            )
        }),
        (_("Footer"), {
            "fields": ("copyright_text",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_at", "updated_at")

    def logo_preview(self, obj):
        return self.preview_image(obj, "logo", width=60, height=60)
    logo_preview.short_description = _("Logo Preview")

    def favicon_preview(self, obj):
        return self.preview_image(obj, "favicon", width=32, height=32)
    favicon_preview.short_description = _("Favicon Preview")

    def hero_default_preview(self, obj):
        return self.preview_image(obj, "hero_default_image", width=100, height=60)
    hero_default_preview.short_description = _("Default Hero Preview")

    list_display = ("church_name", "short_name", "email", "phone", "logo_preview")
    search_fields = ("church_name", "short_name", "email")


# ---------- Homepage Settings ----------
@admin.register(HomepageSettings)
class HomepageSettingsAdmin(SingletonAdmin):
    fieldsets = (
        (_("Hero Section"), {
            "fields": (
                "hero_title", "hero_subtitle", "hero_button_text", "hero_button_link",
            )
        }),
        (_("Welcome Section"), {
            "fields": ("welcome_title", "welcome_message")
        }),
        (_("Featured Content"), {
            "fields": (
                "featured_sermon", "featured_devotional",
                "featured_testimony", "featured_event",
            )
        }),
        (_("Display Options"), {
            "fields": (
                "show_gallery", "show_events", "show_testimonies",
                "show_devotionals", "show_sermons", "show_ministries",
                "show_statistics",
            )
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("__str__", "created_at", "updated_at")
    autocomplete_fields = ("featured_sermon", "featured_devotional", "featured_testimony", "featured_event")


# ---------- Hero Slide ----------
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("Content"), {
            "fields": ("title", "subtitle", "button_text", "button_link")
        }),
        (_("Media"), {
            "fields": ("image", "video_file", "youtube_url")
        }),
        (_("Display"), {
            "fields": ("display_order", "is_active")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("title", "is_active", "display_order", "image_preview", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")
    ordering = ("display_order", "-created_at")
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")
    save_on_top = True
    empty_value_display = "-empty-"

    def image_preview(self, obj):
        return self.preview_image(obj, "image", width=100, height=60)
    image_preview.short_description = _("Image Preview")


# ---------- Announcement ----------
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Content"), {
            "fields": ("title", "content")
        }),
        (_("Display"), {
            "fields": ("is_active", "display_until", "display_order")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("title", "is_active", "display_until", "display_order", "is_displayable")
    list_filter = ("is_active", "display_until")
    search_fields = ("title", "content")
    ordering = ("display_order", "-created_at")
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")
    save_on_top = True

    def is_displayable(self, obj):
        return obj.is_displayable()
    is_displayable.boolean = True
    is_displayable.short_description = _("Displayable")


# ---------- Service Schedule ----------
@admin.register(ServiceSchedule)
class ServiceScheduleAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Schedule"), {
            "fields": ("day", "start_time", "end_time")
        }),
        (_("Details"), {
            "fields": ("name", "venue", "description")
        }),
        (_("Display"), {
            "fields": ("is_active", "display_order")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("name", "day", "start_time", "end_time", "is_active", "display_order")
    list_filter = ("day", "is_active")
    search_fields = ("name", "venue", "description")
    ordering = ("day", "start_time", "display_order")
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")


# ---------- Social Link ----------
@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Link"), {
            "fields": ("platform", "url", "icon_class")
        }),
        (_("Display"), {
            "fields": ("is_active", "display_order")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("platform", "url", "is_active", "display_order")
    list_filter = ("platform", "is_active")
    search_fields = ("url", "icon_class")
    ordering = ("display_order",)
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")


# ---------- Leadership ----------
@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General"), {
            "fields": ("name", "position", "photo", "biography", "quote")
        }),
        (_("Contact & Social"), {
            "fields": ("email", "phone", "facebook", "instagram")
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description", "meta_keywords", "og_image", "canonical_url"),
            "classes": ("collapse",),
        }),
        (_("Display"), {
            "fields": ("display_order", "show_on_homepage")
        }),
        (_("Slug"), {
            "fields": ("slug",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("name", "position", "display_order", "show_on_homepage", "photo_preview")
    list_filter = ("show_on_homepage",)
    search_fields = ("name", "position", "biography")
    ordering = ("display_order", "name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
    save_on_top = True
    # list_select_related = None  # no foreign keys

    def photo_preview(self, obj):
        return self.preview_image(obj, "photo", width=60, height=80)
    photo_preview.short_description = _("Photo Preview")


# ---------- Ministry ----------
@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General"), {
            "fields": ("name", "leader", "image", "description")
        }),
        (_("Meeting Details"), {
            "fields": ("meeting_day", "meeting_time", "meeting_venue")
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description", "meta_keywords", "og_image", "canonical_url"),
            "classes": ("collapse",),
        }),
        (_("Display"), {
            "fields": ("display_order",)
        }),
        (_("Slug"), {
            "fields": ("slug",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("name", "leader", "display_order", "image_preview")
    search_fields = ("name", "leader", "description")
    ordering = ("display_order", "name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
    save_on_top = True

    def image_preview(self, obj):
        return self.preview_image(obj, "image", width=100, height=60)
    image_preview.short_description = _("Image Preview")


# ---------- Sermon Category ----------
@admin.register(SermonCategory)
class SermonCategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("General"), {
            "fields": ("title", "description")
        }),
        (_("Slug"), {
            "fields": ("slug",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("title", "slug", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50


# ---------- Sermon ----------
@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General"), {
            "fields": ("title", "speaker", "category", "bible_reference", "series")
        }),
        (_("Content"), {
            "fields": ("summary", "content")
        }),
        (_("Media"), {
            "fields": ("thumbnail", "youtube_url", "audio_file", "pdf_notes")
        }),
        (_("Publishing"), {
            "fields": ("date_preached", "published", "featured")
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description", "meta_keywords", "og_image", "canonical_url"),
            "classes": ("collapse",),
        }),
        (_("Slug"), {
            "fields": ("slug",)
        }),
        (_("Statistics"), {
            "fields": ("views",),
            "classes": ("collapse",),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("title", "speaker", "category", "date_preached", "published", "featured", "thumbnail_preview")
    list_filter = ("published", "featured", "category", "date_preached")
    search_fields = ("title", "speaker", "bible_reference", "summary", "content")
    ordering = ("-date_preached",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views", "created_at", "updated_at")
    list_per_page = 50
    save_on_top = True
    list_select_related = ("category",)
    date_hierarchy = "date_preached"
    autocomplete_fields = ("category",)

    def thumbnail_preview(self, obj):
        return self.preview_image(obj, "thumbnail", width=100, height=60)
    thumbnail_preview.short_description = _("Thumbnail Preview")

    actions = ["publish_selected", "unpublish_selected", "feature_selected", "unfeature_selected"]

    def publish_selected(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, _(f"{updated} sermons published."))
    publish_selected.short_description = _("Publish selected sermons")

    def unpublish_selected(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, _(f"{updated} sermons unpublished."))
    unpublish_selected.short_description = _("Unpublish selected sermons")

    def feature_selected(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, _(f"{updated} sermons featured."))
    feature_selected.short_description = _("Feature selected sermons")

    def unfeature_selected(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, _(f"{updated} sermons unfeatured."))
    unfeature_selected.short_description = _("Unfeature selected sermons")


# ---------- Event ----------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General"), {
            "fields": ("title", "event_type", "venue", "description")
        }),
        (_("Date & Time"), {
            "fields": ("start_date", "end_date")
        }),
        (_("Media & Links"), {
            "fields": ("banner", "registration_link", "google_maps_link")
        }),
        (_("Publishing"), {
            "fields": ("published", "featured")
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description", "meta_keywords", "og_image", "canonical_url"),
            "classes": ("collapse",),
        }),
        (_("Slug"), {
            "fields": ("slug",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("title", "event_type", "start_date", "end_date", "venue", "published", "featured", "banner_preview")
    list_filter = ("event_type", "published", "featured", "start_date")
    search_fields = ("title", "description", "venue")
    ordering = ("-start_date",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
    save_on_top = True
    date_hierarchy = "start_date"

    def banner_preview(self, obj):
        return self.preview_image(obj, "banner", width=100, height=60)
    banner_preview.short_description = _("Banner Preview")

    actions = ["publish_selected", "unpublish_selected", "feature_selected", "unfeature_selected"]

    def publish_selected(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, _(f"{updated} events published."))
    publish_selected.short_description = _("Publish selected events")

    def unpublish_selected(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, _(f"{updated} events unpublished."))
    unpublish_selected.short_description = _("Unpublish selected events")

    def feature_selected(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, _(f"{updated} events featured."))
    feature_selected.short_description = _("Feature selected events")

    def unfeature_selected(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, _(f"{updated} events unfeatured."))
    unfeature_selected.short_description = _("Unfeature selected events")

@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published",
        "display_order",
        "created_at",
    )

    list_filter = (
        "published",
    )

    search_fields = (
        "title",
        "description",
    )

    ordering = (
        "display_order",
        "-created_at",
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = (
        "caption",
        "album",
        "display_order",
        "created_at",
    )

    list_filter = (
        "album",
    )

    search_fields = (
        "caption",
        "album__title",
    )

    autocomplete_fields = (
        "album",
    )

    ordering = (
        "display_order",
        "-created_at",
    )

# ---------- Testimony ----------
@admin.register(Testimony)
class TestimonyAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General"), {
            "fields": ("full_name", "email", "title", "story")
        }),
        (_("Media"), {
            "fields": ("photo",)
        }),
        (_("Publishing"), {
            "fields": ("approved", "featured", "published_date")
        }),
        (_("SEO"), {
            "fields": ("meta_title", "meta_description", "meta_keywords", "og_image", "canonical_url"),
            "classes": ("collapse",),
        }),
        (_("Slug"), {
            "fields": ("slug",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("full_name", "title", "approved", "featured", "published_date", "photo_preview")
    list_filter = ("approved", "featured", "published_date")
    search_fields = ("full_name", "email", "title", "story")
    ordering = ("-published_date",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
    save_on_top = True
    date_hierarchy = "published_date"

    def photo_preview(self, obj):
        return self.preview_image(obj, "photo", width=60, height=80)
    photo_preview.short_description = _("Photo Preview")

    actions = ["approve_testimonies", "feature_selected", "unfeature_selected"]

    def approve_testimonies(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, _(f"{updated} testimonies approved."))
    approve_testimonies.short_description = _("Approve selected testimonies")

    def feature_selected(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, _(f"{updated} testimonies featured."))
    feature_selected.short_description = _("Feature selected testimonies")

    def unfeature_selected(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, _(f"{updated} testimonies unfeatured."))
    unfeature_selected.short_description = _("Unfeature selected testimonies")


# ---------- Prayer Request ----------
@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Requestor"), {
            "fields": ("full_name", "email", "phone")
        }),
        (_("Request Details"), {
            "fields": ("urgency", "request_details", "confidential")
        }),
        (_("Admin"), {
            "fields": ("status", "admin_notes")
        }),
        (_("Timestamps"), {
            "fields": ("submitted_date", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("full_name", "urgency", "status", "submitted_date", "confidential")
    list_filter = ("urgency", "status", "confidential", "submitted_date")
    search_fields = ("full_name", "email", "phone", "request_details", "admin_notes")
    ordering = ("-submitted_date",)
    readonly_fields = ("submitted_date", "created_at", "updated_at")
    list_per_page = 50
    save_on_top = True
    date_hierarchy = "submitted_date"

    actions = ["mark_prayed", "mark_answered", "mark_archived"]

    def mark_prayed(self, request, queryset):
        updated = queryset.update(status="prayed")
        self.message_user(request, _(f"{updated} prayer requests marked as prayed for."))
    mark_prayed.short_description = _("Mark selected as Prayed For")

    def mark_answered(self, request, queryset):
        updated = queryset.update(status="answered")
        self.message_user(request, _(f"{updated} prayer requests marked as answered."))
    mark_answered.short_description = _("Mark selected as Answered")

    def mark_archived(self, request, queryset):
        updated = queryset.update(status="archived")
        self.message_user(request, _(f"{updated} prayer requests archived."))
    mark_archived.short_description = _("Archive selected")


# ---------- Contact Message ----------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Sender"), {
            "fields": ("full_name", "email", "phone")
        }),
        (_("Message"), {
            "fields": ("subject", "message")
        }),
        (_("Status"), {
            "fields": ("read_status",)
        }),
        (_("Timestamps"), {
            "fields": ("submitted_date", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("full_name", "subject", "email", "read_status", "submitted_date")
    list_filter = ("read_status", "submitted_date")
    search_fields = ("full_name", "email", "subject", "message")
    ordering = ("-submitted_date",)
    readonly_fields = ("submitted_date", "created_at", "updated_at")
    list_per_page = 50
    save_on_top = True
    date_hierarchy = "submitted_date"

    actions = ["mark_read", "mark_unread"]

    def mark_read(self, request, queryset):
        updated = queryset.update(read_status=True)
        self.message_user(request, _(f"{updated} messages marked as read."))
    mark_read.short_description = _("Mark selected as read")

    def mark_unread(self, request, queryset):
        updated = queryset.update(read_status=False)
        self.message_user(request, _(f"{updated} messages marked as unread."))
    mark_unread.short_description = _("Mark selected as unread")


# ---------- Giving Information ----------
@admin.register(GivingInformation)
class GivingInformationAdmin(admin.ModelAdmin, ImagePreviewMixin):
    fieldsets = (
        (_("General"), {
            "fields": ("title", "description")
        }),
        (_("Bank Details"), {
            "fields": ("bank_name", "account_name", "account_number")
        }),
        (_("Media"), {
            "fields": ("qr_image",)
        }),
        (_("Display"), {
            "fields": ("display_order",)
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("title", "bank_name", "account_name", "account_number", "display_order", "qr_preview")
    search_fields = ("title", "bank_name", "account_name", "account_number", "description")
    ordering = ("display_order",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
    save_on_top = True

    def qr_preview(self, obj):
        return self.preview_image(obj, "qr_image", width=60, height=60)
    qr_preview.short_description = _("QR Code")


# ---------- Newsletter Subscriber ----------
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("Subscriber"), {
            "fields": ("name", "email")
        }),
        (_("Status"), {
            "fields": ("active",)
        }),
        (_("Timestamps"), {
            "fields": ("subscribed_date", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    list_display = ("email", "name", "active", "subscribed_date")
    list_filter = ("active", "subscribed_date")
    search_fields = ("email", "name")
    ordering = ("-subscribed_date",)
    readonly_fields = ("subscribed_date", "created_at", "updated_at")
    list_per_page = 50
    save_on_top = True

    actions = ["activate_subscribers", "deactivate_subscribers"]

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, _(f"{updated} subscribers activated."))
    activate_subscribers.short_description = _("Activate selected subscribers")

    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, _(f"{updated} subscribers deactivated."))
    deactivate_subscribers.short_description = _("Deactivate selected subscribers")
@admin.register(Devotional)
class DevotionalAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ("title",)
    list_filter = ("published",)
    list_per_page = 20
    fieldsets = (
    ("Basic Information", {
        "fields": ("title", "slug")
    }),
    ("Content", {
        "fields": ("featured_image", "content")
    }),
    ("Publishing", {
        "fields": ("published", "featured")
    }),
)
 